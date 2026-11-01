import hashlib
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from src.core.models import Chunk, Document, DocumentType, IndexMetadata, ParseQuality
from src.course_update.library_update import (
    list_replacement_backups,
    replace_library_document,
    restore_library_backup,
)


class FakeLoader:
    def __init__(self, course_root: Path, initial_file: Path):
        self.index_name = "demo"
        self.documents = {
            "old_doc": Document(
                "old_doc",
                initial_file.name,
                str(initial_file),
                DocumentType.PDF,
            )
        }
        self.chunks = [Chunk("old_chunk", "old_doc", 0, "old course content")]
        self.metadata = IndexMetadata(
            total_documents=1,
            total_chunks=1,
            document_ids=["old_doc"],
        )
        self.course_root = course_root

    def load_document(self, file_path: str, file_name: str | None = None):
        content = Path(file_path).read_bytes()
        document_id = f"new_{hashlib.sha256(content).hexdigest()[:8]}"
        document = Document(
            document_id=document_id,
            file_name=file_name or Path(file_path).name,
            file_path=file_path,
            document_type=DocumentType.PDF,
            metadata={"original_path": file_path},
            parse_quality=ParseQuality.GOOD,
        )
        chunk = Chunk(f"{document_id}_chunk", document_id, 0, content.decode())
        self.documents[document_id] = document
        self.chunks.append(chunk)
        self.metadata.total_documents = len(self.documents)
        self.metadata.total_chunks = len(self.chunks)
        self.metadata.document_ids = list(self.documents)
        self.metadata.last_updated = datetime.now()
        return document, [chunk]

    def save_index(self, index_path: str):
        Path(index_path).write_text(
            json.dumps({
                "documents": {
                    key: {
                        "file_path": doc.file_path,
                        "file_name": doc.file_name,
                    }
                    for key, doc in self.documents.items()
                },
                "chunks": [chunk.chunk_id for chunk in self.chunks],
            }),
            encoding="utf-8",
        )


class TestLibraryUpdate(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        root = Path(self.temporary_directory.name)
        self.data_dir = root / "data"
        self.course_root = self.data_dir / "demo"
        self.course_root.mkdir(parents=True)
        self.target = self.course_root / "latest.pdf"
        self.target.write_bytes(b"%PDF-old")
        self.replacement = root / "incoming.pdf"
        self.replacement.write_bytes(b"%PDF-new")
        self.index_path = self.data_dir / "index" / "demo.json"
        self.index_path.parent.mkdir()
        self.index_path.write_text("old index", encoding="utf-8")
        self.cache_path = self.data_dir / "index" / "demo_embeddings.npy"
        self.cache_path.write_bytes(b"old embeddings")
        self.loader = FakeLoader(self.course_root, self.target)
        self.config_patches = (
            patch("src.course_update.library_update.Config.DATA_DIR", self.data_dir),
            patch(
                "src.course_update.library_update.Config.get_index_path",
                return_value=self.index_path,
            ),
            patch(
                "src.course_update.library_update.Config.get_embedding_cache_path",
                return_value=self.cache_path,
            ),
        )
        for config_patch in self.config_patches:
            config_patch.start()
            self.addCleanup(config_patch.stop)

    def test_replace_reindexes_invalidates_cache_and_keeps_rollback_backup(self):
        result = replace_library_document(
            self.loader,
            "demo",
            "old_doc",
            self.replacement,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(self.target.read_bytes(), b"%PDF-new")
        self.assertFalse(self.cache_path.exists())
        index = json.loads(self.index_path.read_text(encoding="utf-8"))
        self.assertEqual(len(index["documents"]), 1)
        self.assertTrue(
            all(chunk_id != "old_chunk" for chunk_id in index["chunks"])
        )
        backups = list_replacement_backups("demo")
        self.assertEqual(len(backups), 1)
        self.assertEqual(
            hashlib.sha256(Path(backups[0]["backup_path"]).read_bytes()).hexdigest(),
            result["old_sha256"],
        )

    def test_identical_file_is_a_noop(self):
        self.replacement.write_bytes(self.target.read_bytes())
        result = replace_library_document(
            self.loader,
            "demo",
            "old_doc",
            self.replacement,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(self.target.read_bytes(), b"%PDF-old")
        self.assertTrue(self.cache_path.is_file())
        self.assertEqual(list_replacement_backups("demo"), [])

    def test_failed_index_commit_restores_original_file_and_cache(self):
        import src.course_update.library_update as library_update

        real_replace = library_update.os.replace
        calls = 0

        def fail_index_commit(source, destination):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected index commit failure")
            return real_replace(source, destination)

        with patch(
            "src.course_update.library_update.os.replace",
            side_effect=fail_index_commit,
        ):
            with self.assertRaisesRegex(OSError, "injected"):
                replace_library_document(
                    self.loader,
                    "demo",
                    "old_doc",
                    self.replacement,
                )

        self.assertEqual(self.target.read_bytes(), b"%PDF-old")
        self.assertEqual(self.index_path.read_text(encoding="utf-8"), "old index")
        self.assertEqual(self.cache_path.read_bytes(), b"old embeddings")
        self.assertEqual(list_replacement_backups("demo"), [])

    def test_backup_can_restore_previous_version(self):
        replaced = replace_library_document(
            self.loader,
            "demo",
            "old_doc",
            self.replacement,
        )
        fresh_loader = FakeLoader(self.course_root, self.target)
        fresh_loader.documents["old_doc"].file_path = str(self.target)
        fresh_loader.documents["old_doc"].document_id = (
            next(iter(json.loads(self.index_path.read_text())["documents"]))
        )
        active_id = next(iter(json.loads(self.index_path.read_text())["documents"]))
        fresh_loader.documents = {active_id: Document(
            active_id,
            self.target.name,
            str(self.target),
            DocumentType.PDF,
        )}
        fresh_loader.chunks = [Chunk("new_chunk", active_id, 0, "current")]

        restored = restore_library_backup(
            fresh_loader,
            "demo",
            str(replaced["backup_id"]),
        )

        self.assertTrue(restored["changed"])
        self.assertEqual(self.target.read_bytes(), b"%PDF-old")
        self.assertTrue(self.cache_path.exists() is False)


if __name__ == "__main__":
    unittest.main()
