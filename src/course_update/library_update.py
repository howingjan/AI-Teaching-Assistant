"""Transactional replacement of a course-library PDF."""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from src.core.config import Config

logger = logging.getLogger(__name__)


def _course_root(course: str) -> Path:
    if not course or Path(course).name != course or course in {".", ".."}:
        raise ValueError("无效的课程目录名。")
    data_root = Config.DATA_DIR.resolve()
    course_root = (data_root / course).resolve()
    if course_root.parent != data_root:
        raise ValueError("课程目录必须位于本地 data 目录下。")
    return course_root


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _temporary_path(directory: Path, suffix: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=".course-update-",
        suffix=suffix,
        dir=directory,
    )
    os.close(descriptor)
    return Path(name)


def list_replacement_backups(course: str) -> list[dict[str, str]]:
    """Return valid, newest-first replacement snapshots for a course."""
    _course_root(course)
    data_root = Config.DATA_DIR.resolve()
    backup_root = data_root / "course_update_backups" / course
    if backup_root.resolve().parent.parent != data_root:
        raise ValueError("版本备份目录必须位于本地 data 目录下。")
    if not backup_root.is_dir():
        return []

    backups = []
    for manifest_path in backup_root.glob("*/manifest.json"):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            backup_file = (manifest_path.parent / manifest["backup_file"]).resolve()
            if (
                manifest.get("course") != course
                or backup_file.parent != manifest_path.parent.resolve()
                or not backup_file.is_file()
                or _sha256(backup_file) != manifest.get("sha256")
            ):
                continue
            backups.append({**manifest, "backup_path": str(backup_file)})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            logger.warning("Ignoring invalid course backup %s: %s", manifest_path, exc)
    return sorted(backups, key=lambda backup: backup["created_at"], reverse=True)


def replace_library_document(
    loader,
    course: str,
    document_id: str,
    replacement_path: str | Path,
) -> dict[str, str | bool]:
    """Replace one indexed PDF, atomically persisting the file and rebuilt index.

    A persistent copy of the previous PDF is retained for a later rollback.
    The caller must explicitly obtain teacher confirmation before calling this.
    """
    if document_id not in loader.documents:
        raise ValueError("所选资料已不在当前索引中，请刷新资料库后重试。")

    course_root = _course_root(course)
    replacement = Path(replacement_path).resolve()
    current_document = loader.documents[document_id]
    target = Path(current_document.file_path).resolve()

    if not course_root.is_dir() or not target.is_relative_to(course_root):
        raise ValueError("目标文件不在所选课程资料目录内，已拒绝替换。")
    if target.suffix.lower() != ".pdf" or replacement.suffix.lower() != ".pdf":
        raise ValueError("课程资料库目前只允许替换 PDF 文件。")
    if not target.is_file() or not replacement.is_file():
        raise FileNotFoundError("待替换文件或新课件不存在。")
    if target.name.casefold() != current_document.file_name.casefold():
        raise ValueError("索引中的文件名与实际文件路径不一致，已拒绝替换。")

    old_hash = _sha256(target)
    new_hash = _sha256(replacement)
    if old_hash == new_hash:
        return {
            "changed": False,
            "message": "新旧文件内容完全相同，无需更新资料库。",
            "old_sha256": old_hash,
            "new_sha256": new_hash,
        }

    candidate = copy.deepcopy(loader)
    del candidate.documents[document_id]
    candidate.chunks = [
        chunk for chunk in candidate.chunks
        if chunk.document_id != document_id
    ]
    candidate.metadata.total_documents = len(candidate.documents)
    candidate.metadata.total_chunks = len(candidate.chunks)
    candidate.metadata.document_ids = list(candidate.documents)

    new_document, new_chunks = candidate.load_document(
        str(replacement),
        file_name=current_document.file_name,
    )
    if _sha256(replacement) != new_hash:
        raise ValueError("新课件在解析期间发生变化，请重新上传后重试。")
    if not new_chunks:
        raise ValueError("新课件没有生成任何可检索文本片段，资料库保持不变。")
    if new_document.document_id in loader.documents:
        raise ValueError("新课件与资料库中的另一份资料内容相同，无法安全区分版本。")
    new_document.file_path = str(target)
    original_path = new_document.metadata.get("original_path")
    if original_path:
        new_document.metadata["original_path"] = str(target)

    index_path = Config.get_index_path(course)
    cache_path = Config.get_embedding_cache_path(course)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_temp = _temporary_path(index_path.parent, ".json")
    target_temp = _temporary_path(target.parent, ".pdf")
    backup_file: Path | None = None
    backup_index: Path | None = None
    backup_cache: Path | None = None
    retained_backup_dir: Path | None = None
    file_committed = False
    index_committed = False
    cache_invalidated = False

    try:
        shutil.copyfile(replacement, target_temp)
        if _sha256(target_temp) != new_hash:
            raise ValueError("新课件在准备提交时发生变化，资料库保持不变。")
        candidate.save_index(str(index_temp))

        backup_root = Config.DATA_DIR / "course_update_backups" / course
        retained_backup_dir = backup_root / uuid.uuid4().hex
        retained_backup_dir.mkdir(parents=True, exist_ok=False)
        retained_backup = retained_backup_dir / target.name
        shutil.copy2(target, retained_backup)
        if _sha256(retained_backup) != old_hash:
            raise ValueError("现有课件在创建备份期间发生变化，已取消替换。")
        manifest = {
            "backup_id": retained_backup_dir.name,
            "course": course,
            "document_id": document_id,
            "file_name": target.name,
            "target_relative_path": str(target.relative_to(course_root)),
            "backup_file": retained_backup.name,
            "sha256": old_hash,
            "created_at": datetime.now().astimezone().isoformat(),
        }
        manifest_temp = retained_backup_dir / ".manifest.tmp"
        manifest_temp.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(manifest_temp, retained_backup_dir / "manifest.json")

        backup_index = _temporary_path(index_path.parent, ".backup")
        if index_path.exists():
            shutil.copy2(index_path, backup_index)
        else:
            backup_index.unlink()
            backup_index = None
        if cache_path.exists():
            backup_cache = _temporary_path(cache_path.parent, ".backup")
            shutil.copy2(cache_path, backup_cache)

        if _sha256(target) != old_hash:
            raise ValueError("现有课件在准备提交期间发生变化，已取消替换。")
        os.replace(target_temp, target)
        file_committed = True
        os.replace(index_temp, index_path)
        index_committed = True
        if cache_path.exists():
            cache_path.unlink()
            cache_invalidated = True

        return {
            "changed": True,
            "message": "课程资料已安全替换；旧版本备份可用于回滚。",
            "old_sha256": old_hash,
            "new_sha256": new_hash,
            "backup_id": retained_backup_dir.name,
        }
    except Exception as exc:
        rollback_errors = []
        if file_committed:
            try:
                if backup_file is None:
                    backup_file = _temporary_path(target.parent, ".rollback")
                    shutil.copy2(retained_backup_dir / target.name, backup_file)
                os.replace(backup_file, target)
                backup_file = None
            except Exception as rollback_exc:
                rollback_errors.append(f"恢复原 PDF 失败：{rollback_exc}")
                logger.exception("Course-library document rollback failed")
        if index_committed:
            try:
                if backup_index is not None and backup_index.exists():
                    os.replace(backup_index, index_path)
                    backup_index = None
                else:
                    index_path.unlink(missing_ok=True)
            except Exception as rollback_exc:
                rollback_errors.append(f"恢复旧索引失败：{rollback_exc}")
                logger.exception("Course-library index rollback failed")
        if cache_invalidated and backup_cache is not None and backup_cache.exists():
            try:
                os.replace(backup_cache, cache_path)
                backup_cache = None
            except Exception as rollback_exc:
                rollback_errors.append(f"恢复 embedding 缓存失败：{rollback_exc}")
                logger.exception("Course-library embedding-cache rollback failed")
        if rollback_errors:
            raise RuntimeError(
                f"资料库替换失败：{exc}；自动回滚也失败，请保留并检查备份目录 "
                f"{retained_backup_dir}。"
            ) from exc
        if retained_backup_dir is not None:
            shutil.rmtree(retained_backup_dir, ignore_errors=True)
        raise
    finally:
        for path in (index_temp, target_temp, backup_file, backup_index, backup_cache):
            if path is not None:
                path.unlink(missing_ok=True)


def restore_library_backup(loader, course: str, backup_id: str) -> dict[str, str | bool]:
    """Restore a prior PDF snapshot through the same validated replacement path."""
    if not backup_id or Path(backup_id).name != backup_id:
        raise ValueError("无效的备份 ID。")
    backup = next(
        (
            item for item in list_replacement_backups(course)
            if item["backup_id"] == backup_id
        ),
        None,
    )
    if backup is None:
        raise ValueError("备份不存在或校验失败，请刷新后重试。")

    course_root = _course_root(course)
    target = (course_root / backup["target_relative_path"]).resolve()
    if not target.is_relative_to(course_root):
        raise ValueError("备份目标路径无效，已拒绝恢复。")
    matching_documents = [
        document_id
        for document_id, document in loader.documents.items()
        if Path(document.file_path).resolve() == target
    ]
    if len(matching_documents) != 1:
        raise ValueError("备份对应的资料未能唯一匹配当前索引，请先刷新资料库。")
    return replace_library_document(
        loader,
        course,
        matching_documents[0],
        backup["backup_path"],
    )
