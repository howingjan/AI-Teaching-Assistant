"""Optional, locally executed DOCX-to-PDF conversion."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pdfplumber


def detect_pdf_converter() -> str | None:
    """Return the LibreOffice executable when available."""
    return shutil.which("soffice") or shutil.which("libreoffice")


def export_docx_to_pdf(
    docx_path: str | Path,
    output_path: str | Path,
    timeout_seconds: int = 120,
) -> Path:
    """Convert a DOCX using LibreOffice, validate the PDF, and atomically publish it."""
    source = Path(docx_path).resolve()
    destination = Path(output_path).resolve()
    converter = detect_pdf_converter()
    if converter is None:
        raise RuntimeError(
            "未检测到 LibreOffice（soffice/libreoffice）。DOCX 已保留；"
            "安装 LibreOffice 后可重新导出 PDF。"
        )
    if not source.is_file() or source.suffix.lower() != ".docx":
        raise ValueError("PDF 导出输入必须是存在的 DOCX 文件。")
    if destination.suffix.lower() != ".pdf":
        raise ValueError("PDF 导出目标扩展名必须为 .pdf。")
    if source == destination:
        raise ValueError("PDF 输出路径不能与源 DOCX 相同。")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="course-update-pdf-") as temporary_dir:
        temporary_root = Path(temporary_dir)
        profile_dir = temporary_root / "lo-profile"
        output_dir = temporary_root / "converted"
        output_dir.mkdir()
        generated_pdf = output_dir / f"{source.stem}.pdf"
        command = [
            converter,
            "--headless",
            "--nologo",
            "--nodefault",
            "--nolockcheck",
            "--norestore",
            f"-env:UserInstallation={profile_dir.as_uri()}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(source),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"PDF 转换超过 {timeout_seconds} 秒，DOCX 文件未受影响。"
            ) from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()
            raise RuntimeError(
                f"LibreOffice 转换失败（退出码 {completed.returncode}）："
                f"{detail or '没有提供错误详情'}"
            )
        if not generated_pdf.is_file() or generated_pdf.stat().st_size <= 0:
            raise RuntimeError("转换器未生成有效 PDF，DOCX 文件已保留。")
        if not generated_pdf.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError("转换器输出不是有效 PDF，DOCX 文件已保留。")
        try:
            with pdfplumber.open(generated_pdf) as document:
                if not document.pages:
                    raise RuntimeError("转换器生成的 PDF 不包含页面。")
        except Exception as exc:
            raise RuntimeError(f"PDF 输出校验失败：{exc}") from exc

        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".course-update-export-",
            suffix=".pdf",
            dir=destination.parent,
        )
        os.close(descriptor)
        temporary_destination = Path(temporary_name)
        try:
            shutil.copyfile(generated_pdf, temporary_destination)
            os.replace(temporary_destination, destination)
        finally:
            temporary_destination.unlink(missing_ok=True)

    return destination
