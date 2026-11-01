import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.course_update.pdf_export import export_docx_to_pdf


class TestPdfExport(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        root = Path(self.temporary_directory.name)
        self.source = root / "lesson.docx"
        self.source.write_bytes(b"original DOCX bytes")
        self.destination = root / "lesson.pdf"

    def test_missing_converter_reports_that_docx_is_preserved(self):
        with patch("src.course_update.pdf_export.detect_pdf_converter", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "DOCX 已保留"):
                export_docx_to_pdf(self.source, self.destination)

        self.assertEqual(self.source.read_bytes(), b"original DOCX bytes")
        self.assertFalse(self.destination.exists())

    def test_successful_conversion_validates_and_atomically_writes_pdf(self):
        def convert(command, **kwargs):
            output_dir = Path(command[command.index("--outdir") + 1])
            (output_dir / "lesson.pdf").write_bytes(b"%PDF-valid-result")
            self.assertFalse(kwargs["shell"])
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        pdf_document = MagicMock()
        pdf_document.__enter__.return_value.pages = [object()]
        pdf_document.__exit__.return_value = None
        with (
            patch("src.course_update.pdf_export.detect_pdf_converter", return_value="/usr/bin/soffice"),
            patch("src.course_update.pdf_export.subprocess.run", side_effect=convert),
            patch("src.course_update.pdf_export.pdfplumber.open", return_value=pdf_document),
        ):
            result = export_docx_to_pdf(self.source, self.destination)

        self.assertEqual(result, self.destination.resolve())
        self.assertEqual(self.destination.read_bytes(), b"%PDF-valid-result")
        self.assertEqual(self.source.read_bytes(), b"original DOCX bytes")

    def test_failed_conversion_does_not_replace_existing_pdf(self):
        self.destination.write_bytes(b"%PDF-previous")
        with (
            patch("src.course_update.pdf_export.detect_pdf_converter", return_value="/usr/bin/soffice"),
            patch(
                "src.course_update.pdf_export.subprocess.run",
                return_value=SimpleNamespace(
                    returncode=1,
                    stdout="",
                    stderr="conversion failed",
                ),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "conversion failed"):
                export_docx_to_pdf(self.source, self.destination)

        self.assertEqual(self.destination.read_bytes(), b"%PDF-previous")
        self.assertEqual(self.source.read_bytes(), b"original DOCX bytes")

    def test_converter_without_output_reports_failure(self):
        with (
            patch("src.course_update.pdf_export.detect_pdf_converter", return_value="/usr/bin/soffice"),
            patch(
                "src.course_update.pdf_export.subprocess.run",
                return_value=SimpleNamespace(returncode=0, stdout="", stderr=""),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "未生成有效 PDF"):
                export_docx_to_pdf(self.source, self.destination)

        self.assertFalse(self.destination.exists())
        self.assertEqual(self.source.read_bytes(), b"original DOCX bytes")

    def test_timeout_reports_failure_and_preserves_docx(self):
        with (
            patch("src.course_update.pdf_export.detect_pdf_converter", return_value="/usr/bin/soffice"),
            patch(
                "src.course_update.pdf_export.subprocess.run",
                side_effect=subprocess.TimeoutExpired("soffice", 1),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "超过 120 秒"):
                export_docx_to_pdf(self.source, self.destination)

        self.assertFalse(self.destination.exists())
        self.assertEqual(self.source.read_bytes(), b"original DOCX bytes")


if __name__ == "__main__":
    unittest.main()
