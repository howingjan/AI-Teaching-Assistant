"""
Failure case library (Phase 4).

The product plan (section 7.3) explicitly requires keeping failure cases —
not just success screenshots — as portfolio evidence:

  - PDF 解析失败
  - 检索到了相似但错误的章节
  - 模型给出资料中没有的结论
  - 引用页码错误
  - 课件和作业要求不一致
  - cheat sheet 内容超出篇幅
  - API 超时或模型不可用

This module persists those failures as structured records under
data/output/failures/ so they can be revisited, explained, and tied to the
resolution (or the fix that reduced the failure rate in the eval report).

FailureLibrary is also used by examples/demo_phase4.py to auto-collect failures
during an evaluation run (failed cases, citation errors, out-of-scope non-
refusals, and needs_review notes that signal material problems).
"""

import json
import logging
from dataclasses import dataclass, field, asdict, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.config import Config

logger = logging.getLogger(__name__)

# Failure type taxonomy (maps to plan section 7.3).
FAILURE_TYPES = {
    "parse_error": "PDF/文档解析失败",
    "retrieval_error": "检索到相似但错误的章节",
    "citation_error": "引用页码或文档错误",
    "hallucination": "模型给出资料中没有的结论",
    "out_of_scope": "资料外问题未被拒答",
    "consistency": "课件与作业要求不一致",
    "page_limit": "cheat sheet 超出篇幅限制",
    "api_error": "API 超时或模型不可用",
    "pipeline_error": "生成流程异常",
}


@dataclass
class FailureRecord:
    """A single documented failure case."""
    type: str  # key from FAILURE_TYPES
    title: str
    description: str = ""
    how_detected: str = ""
    root_cause: str = ""
    resolution: str = ""
    course: str = ""
    task: str = ""
    evidence_path: str = ""
    date: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def __post_init__(self):
        if self.type not in FAILURE_TYPES:
            raise ValueError(f"Unknown failure type: {self.type}")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["type_label"] = FAILURE_TYPES.get(self.type, self.type)
        return data


class FailureLibrary:
    """
    A JSON + Markdown backed collection of failure records.

    Args:
        json_path: Path of the JSON store.
        md_path: Path of the human-readable Markdown store.
    """

    def __init__(
        self,
        json_path: Optional[Path] = None,
        md_path: Optional[Path] = None,
    ):
        self.json_path = json_path or Config.get_output_path(
            "failures.json", subdir="failures"
        )
        self.md_path = md_path or Config.get_output_path(
            "failures.md", subdir="failures"
        )
        self.records: List[FailureRecord] = []
        self._load()

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(
        self,
        failure_type: str,
        title: str,
        description: str = "",
        how_detected: str = "",
        root_cause: str = "",
        resolution: str = "",
        course: str = "",
        task: str = "",
        evidence_path: str = "",
        dedupe: bool = True,
    ) -> FailureRecord:
        """Add a failure record. When dedupe=True, identical (type, title)
        records are updated instead of duplicated."""
        if dedupe:
            for existing in self.records:
                if existing.type == failure_type and existing.title == title:
                    existing.description = description or existing.description
                    existing.how_detected = how_detected or existing.how_detected
                    existing.root_cause = root_cause or existing.root_cause
                    existing.resolution = resolution or existing.resolution
                    existing.course = course or existing.course
                    existing.task = task or existing.task
                    if evidence_path:
                        existing.evidence_path = evidence_path
                    return existing

        record = FailureRecord(
            type=failure_type,
            title=title,
            description=description,
            how_detected=how_detected,
            root_cause=root_cause,
            resolution=resolution,
            course=course,
            task=task,
            evidence_path=evidence_path,
        )
        self.records.append(record)
        return record

    def add_many(self, records: List[FailureRecord]) -> int:
        """Add several records, deduplicating by (type, title). Returns the
        number of new records added."""
        added = 0
        for r in records:
            if self.add(
                r.type,
                r.title,
                r.description,
                r.how_detected,
                r.root_cause,
                r.resolution,
                r.course,
                r.task,
                r.evidence_path,
            ) is not None:
                added += 1
        return added

    def remove(self, title: str) -> bool:
        """Remove the first record matching title. Returns True if removed."""
        for i, r in enumerate(self.records):
            if r.title == title:
                del self.records[i]
                return True
        return False

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> Dict[str, Path]:
        """Persist the library to JSON and Markdown. Returns written paths."""
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(self.to_json(), encoding="utf-8")
        self.md_path.write_text(self.to_markdown(), encoding="utf-8")
        return {"json": self.json_path, "markdown": self.md_path}

    def _load(self) -> None:
        if not self.json_path.exists():
            return
        try:
            data = json.loads(self.json_path.read_text(encoding="utf-8"))
            allowed = {f.name for f in fields(FailureRecord)}
            for item in data.get("records", []):
                try:
                    # Drop derived keys (e.g. type_label from to_dict) that are
                    # not dataclass fields so the record round-trips cleanly.
                    record = FailureRecord(**{
                        k: v for k, v in item.items() if k in allowed
                    })
                    self.records.append(record)
                except (TypeError, ValueError) as exc:
                    logger.warning(f"Skipping malformed failure record: {exc}")
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"Failed to load failure library: {exc}")

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def to_json(self) -> str:
        return json.dumps(
            {"count": len(self.records), "records": [r.to_dict() for r in self.records]},
            ensure_ascii=False,
            indent=2,
        )

    def to_markdown(self) -> str:
        if not self.records:
            return "# 失败案例库\n\n_（暂无记录）_\n"

        lines = ["# 失败案例库", ""]
        lines.append(f"共 {len(self.records)} 条记录。")
        lines.append("")

        by_type: Dict[str, List[FailureRecord]] = {}
        for r in self.records:
            by_type.setdefault(r.type, []).append(r)

        lines.append("## 按类型统计")
        lines.append("")
        lines.append("| 类型 | 数量 |")
        lines.append("|------|------|")
        for ftype in FAILURE_TYPES:
            count = len(by_type.get(ftype, []))
            if count:
                lines.append(f"| {FAILURE_TYPES[ftype]} | {count} |")
        lines.append("")

        lines.append("## 记录明细")
        lines.append("")
        for r in self.records:
            lines.append(f"### {FAILURE_TYPES.get(r.type, r.type)}：{r.title}")
            lines.append("")
            lines.append(f"- **日期**：{r.date}")
            if r.course:
                lines.append(f"- **课程**：{r.course}")
            if r.task:
                lines.append(f"- **任务**：{r.task}")
            if r.description:
                lines.append(f"- **现象描述**：{r.description}")
            if r.how_detected:
                lines.append(f"- **如何发现**：{r.how_detected}")
            if r.root_cause:
                lines.append(f"- **根因**：{r.root_cause}")
            if r.resolution:
                lines.append(f"- **处理/修复**：{r.resolution}")
            if r.evidence_path:
                lines.append(f"- **证据**：`{r.evidence_path}`")
            lines.append("")
        return "\n".join(lines).strip() + "\n"
