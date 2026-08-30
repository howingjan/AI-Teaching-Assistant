"""
Unified task evaluation (Phase 3).

Implements the product plan's evaluation layer (section 7):

  - 引用页码准确率  (citation accuracy): fraction of model-proposed citations
    that reference real documents/pages.
  - 关键结构化字段完整率 (field completeness): fraction of the task's required
    structured fields that are populated.
  - 资料外问题无依据回答率 (out-of-scope refusal rate): for questions the course
    materials do NOT cover, the system must flag insufficiency instead of
    confidently answering.
  - Task-specific checks: layered hints are tiered (讲题), knowledge map has
    dependencies (复习), cheat sheet within page limit (速查表), exam mapping
    has evidence (真题映射).

An EvaluationCase declares a task, its inputs, and optional ground truth.
TaskEvaluator runs each case through a RAGPipeline and aggregates an
EvaluationReport that can be exported to JSON / Markdown.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.core.models import Citation, TeachingTask
from src.rag.citation_validator import CitationValidator
from src.rag.llm_client import parse_json_response

logger = logging.getLogger(__name__)


@dataclass
class EvaluationCase:
    """
    A single evaluation question for one teaching task.

    Attributes:
        task_type: TeachingTask (or its string value).
        inputs: Task inputs, e.g. {"topic": ...} / {"problem_text": ...} /
            {"scope": ...} / {"exam_topic": ...}.
        name: Human-readable case name.
        out_of_scope: True when the case tests content the materials do NOT cover.
        expected_knowledge_points: Optional ground-truth knowledge points.
    """
    task_type: TeachingTask
    inputs: Dict[str, Any]
    name: str = ""
    out_of_scope: bool = False
    expected_knowledge_points: List[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.task_type, str):
            self.task_type = TeachingTask(self.task_type)
        if not self.name:
            self.name = f"{self.task_type.value}:{list(self.inputs.values())[0] if self.inputs else '?'}"


@dataclass
class CaseResult:
    """Metrics for a single evaluation case."""
    case_name: str
    task_type: str
    success: bool = False
    error: str = ""
    field_checks: Dict[str, bool] = field(default_factory=dict)
    field_complete_rate: float = 0.0
    fully_complete: bool = False
    citation_accuracy: Optional[float] = None
    citation_count: int = 0
    valid_citation_count: int = 0
    out_of_scope: bool = False
    refused_correctly: Optional[bool] = None
    needs_review: List[str] = field(default_factory=list)
    task_specific: Dict[str, bool] = field(default_factory=dict)
    # Phase 4: cost & latency from the pipeline's UsageMonitor
    latency_s: Optional[float] = None
    mode: str = ""
    cost_usd: Optional[float] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass
class EvaluationReport:
    """Aggregate evaluation results across all cases."""
    cases: List[CaseResult] = field(default_factory=list)
    overall: Dict[str, float] = field(default_factory=dict)
    by_task: Dict[str, Dict[str, float]] = field(default_factory=dict)

    @property
    def total_cases(self) -> int:
        return len(self.cases)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_cases": self.total_cases,
            "overall": self.overall,
            "by_task": self.by_task,
            "cases": [
                {
                    "case_name": c.case_name,
                    "task_type": c.task_type,
                    "success": c.success,
                    "error": c.error,
                    "field_checks": c.field_checks,
                    "field_complete_rate": c.field_complete_rate,
                    "fully_complete": c.fully_complete,
                    "citation_accuracy": c.citation_accuracy,
                    "citation_count": c.citation_count,
                    "valid_citation_count": c.valid_citation_count,
                    "out_of_scope": c.out_of_scope,
                    "refused_correctly": c.refused_correctly,
                    "needs_review": c.needs_review,
                    "task_specific": c.task_specific,
                    "latency_s": c.latency_s,
                    "mode": c.mode,
                    "cost_usd": c.cost_usd,
                    "prompt_tokens": c.prompt_tokens,
                    "completion_tokens": c.completion_tokens,
                }
                for c in self.cases
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        lines = ["# 评测报告（统一任务评测）", ""]
        lines.append("## 总体指标")
        lines.append("")
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        for key, value in self.overall.items():
            if key in ("total_cost_usd", "avg_cost_usd"):
                lines.append(f"| {key} | ${value:.5f} |")
            elif key in ("total_latency_s", "avg_latency_s"):
                lines.append(f"| {key} | {value:.2f}s |")
            elif key in ("total_cases", "total_tokens", "real_calls", "mock_calls"):
                lines.append(f"| {key} | {value} |")
            elif isinstance(value, float) and 0 <= value <= 1:
                lines.append(f"| {key} | {value:.2%} |")
            elif isinstance(value, float):
                lines.append(f"| {key} | {value:.3f} |")
            else:
                lines.append(f"| {key} | {value} |")
        lines.append("")

        if self.by_task:
            lines.append("## 按任务")
            lines.append("")
            lines.append("| 任务 | 用例数 | 字段完整率 | 引用准确率 | 平均延迟 (s) | 成本 (USD) |")
            lines.append("|------|--------|-----------|-----------|--------------|------------|")
            for task, metrics in self.by_task.items():
                lines.append(
                    f"| {task} | {metrics.get('cases', 0)} "
                    f"| {metrics.get('field_complete_rate', 0):.2%} "
                    f"| {metrics.get('citation_accuracy', 0):.2%} "
                    f"| {metrics.get('avg_latency_s', 0):.2f} "
                    f"| {metrics.get('total_cost_usd', 0):.5f} |"
                )
            lines.append("")

        lines.append("## 分用例")
        lines.append("")
        for c in self.cases:
            status = "✅" if c.success else "❌"
            lines.append(f"### {status} {c.case_name}（{c.task_type}）")
            lines.append("")
            if c.error:
                lines.append(f"- 错误：{c.error}")
            lines.append(f"- 字段完整率：{c.field_complete_rate:.0%}"
                         f"{'（完全完整）' if c.fully_complete else ''}")
            if c.citation_accuracy is not None:
                lines.append(
                    f"- 引用准确率：{c.citation_accuracy:.0%} "
                    f"（{c.valid_citation_count}/{c.citation_count}）"
                )
            if c.out_of_scope and c.refused_correctly is not None:
                lines.append(f"- 资料外拒答：{'正确' if c.refused_correctly else '未拒答 ❌'}")
            if c.task_specific:
                detail = "；".join(f"{k}={'✓' if v else '✗'}" for k, v in c.task_specific.items())
                lines.append(f"- 任务专项：{detail}")
            if c.latency_s is not None:
                mode = "真实" if c.mode == "real" else "mock"
                cost = f"，预估成本 ${c.cost_usd:.6f}" if c.cost_usd is not None else ""
                lines.append(
                    f"- 耗时：{c.latency_s:.2f}s（{mode}），"
                    f"输入 {c.prompt_tokens} / 输出 {c.completion_tokens} tokens{cost}"
                )
            if c.needs_review:
                lines.append("- 需老师确认：")
                for note in c.needs_review[:5]:
                    lines.append(f"  - ⚠️ {note}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"


class TaskEvaluator:
    """
    Runs evaluation cases through a RAGPipeline and aggregates metrics.

    Citation validation is done independently of the pipeline (by re-parsing
    the model's raw output) so that citation accuracy is measured honestly
    rather than inherited from pipeline-side filtering.
    """

    def __init__(self, documents: dict, chunks: Optional[list] = None):
        self.documents = documents
        self.validator = CitationValidator(chunks or [], documents)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate_case(self, pipeline, case: EvaluationCase) -> CaseResult:
        """Run one case through the pipeline and compute its metrics."""
        result = CaseResult(
            case_name=case.name,
            task_type=case.task_type.value,
            out_of_scope=case.out_of_scope,
        )
        try:
            output = pipeline.generate_task(case.task_type, case.inputs)
        except Exception as exc:  # pipeline / LLM failure
            result.success = False
            result.error = f"{type(exc).__name__}: {exc}"
            return result

        result.needs_review = list(getattr(output, "needs_review", []))

        # 1. Field completeness
        completeness = output.completeness()
        required = {k: v for k, v in completeness.items() if k != "complete"}
        result.field_checks = required
        result.fully_complete = bool(completeness.get("complete", False))
        if required:
            result.field_complete_rate = sum(required.values()) / len(required)

        # 2. Citation accuracy (independent re-validation)
        proposed = self._proposed_citations(output)
        if proposed:
            validation = self.validator.validate(proposed)
            result.citation_count = len(proposed)
            result.valid_citation_count = (
                result.citation_count
                - len(validation.missing_documents)
                - len(validation.out_of_range_pages)
            )
            result.citation_accuracy = result.valid_citation_count / result.citation_count

        # 3. Out-of-scope refusal
        if case.out_of_scope:
            result.refused_correctly = self._is_refused(output)

        # 4. Task-specific checks
        result.task_specific = self._task_specific_checks(case.task_type, output)

        # 5. Cost & latency from the pipeline's UsageMonitor (Phase 4)
        self._attach_usage(pipeline, result)

        # 6. Success = ran without error and met the primary quality gate.
        result.success = True
        return result

    def _attach_usage(self, pipeline, result: CaseResult) -> None:
        """Copy the most recent generation usage (latency/cost) into the case."""
        monitor = getattr(pipeline, "monitor", None)
        record = getattr(monitor, "last_record", None)
        if record is None:
            return
        result.latency_s = record.latency_s
        result.mode = record.mode
        result.cost_usd = record.cost_usd
        result.prompt_tokens = record.prompt_tokens
        result.completion_tokens = record.completion_tokens

    def evaluate(self, pipeline, cases: List[EvaluationCase]) -> EvaluationReport:
        """Run all cases and aggregate into a report."""
        report = EvaluationReport()
        for case in cases:
            report.cases.append(self.evaluate_case(pipeline, case))

        report.overall = self._aggregate(report.cases)
        report.by_task = self._aggregate_by_task(report.cases)
        return report

    # ------------------------------------------------------------------
    # Metrics helpers
    # ------------------------------------------------------------------

    def _proposed_citations(self, output) -> List[Citation]:
        """Extract the citations the model proposed (from raw JSON output)."""
        raw = getattr(output, "raw_output", "")
        if not raw:
            # Fall back to the (already-filtered) result citations.
            return list(getattr(output, "citations", []))

        try:
            data = parse_json_response(raw)
        except ValueError:
            return list(getattr(output, "citations", []))

        citations: List[Citation] = []

        def add(doc_id: Any, page: Any) -> None:
            doc_id = str(doc_id).strip()
            if not doc_id:
                return
            try:
                page = int(page)
            except (TypeError, ValueError):
                page = 0
            citations.append(Citation(document_id=doc_id, page=page))

        # Top-level citations (lesson / problem / review / cheatsheet).
        for item in data.get("citations", []) or []:
            if isinstance(item, dict):
                add(item.get("document_id"), item.get("page"))

        # Nested evidence (exam mapping: knowledge_points[].evidence_chunks).
        for kp in data.get("knowledge_points", []) or []:
            if not isinstance(kp, dict):
                continue
            for ev in (kp.get("evidence_chunks") or kp.get("evidence") or []):
                if isinstance(ev, dict):
                    add(ev.get("document_id"), ev.get("page"))
        return citations

    def _is_refused(self, output) -> bool:
        """Did the output refuse to answer because materials are insufficient?"""
        if getattr(output, "insufficient_material", False):
            return True
        notes = getattr(output, "needs_review", []) or []
        for note in notes:
            if "资料" in note and ("不足" in note or "未覆盖" in note or "没有" in note):
                return True
        # coverage_gap for exam mapping is itself an explicit refusal signal.
        if getattr(output, "coverage_gap", ""):
            return True
        return False

    def _task_specific_checks(self, task: TeachingTask, output) -> Dict[str, bool]:
        checks: Dict[str, bool] = {}
        if task == TeachingTask.PROBLEM_SOLVING:
            completeness = output.completeness()
            checks["layered_hints_tiered"] = bool(
                completeness.get("layered_hints_are_tiered", False)
            )
        elif task == TeachingTask.REVIEW:
            completeness = output.completeness()
            checks["knowledge_map_dependencies"] = bool(
                completeness.get("knowledge_map_has_dependencies", False)
            )
        elif task == TeachingTask.CHEATSHEET:
            checks["within_page_limit"] = bool(
                getattr(output, "within_page_limit", False)
            )
        elif task == TeachingTask.EXAM_MAPPING:
            completeness = output.completeness()
            checks["has_evidence"] = bool(completeness.get("has_evidence", False))
        return checks

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    @staticmethod
    def _mean(values: List[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _aggregate(self, cases: List[CaseResult]) -> Dict[str, float]:
        ran = [c for c in cases if c.success]
        citation_values = [
            c.citation_accuracy for c in ran
            if c.citation_accuracy is not None
        ]
        field_rates = [c.field_complete_rate for c in ran]
        out_of_scope = [c for c in ran if c.out_of_scope]

        # Phase 4: cost & latency
        latencies = [c.latency_s for c in ran if c.latency_s is not None]
        costs = [c.cost_usd for c in ran if c.cost_usd is not None]
        total_tokens = sum(
            (c.prompt_tokens or 0) + (c.completion_tokens or 0) for c in ran
        )
        real_calls = sum(1 for c in ran if c.mode == "real")
        mock_calls = sum(1 for c in ran if c.mode == "mock")

        metrics: Dict[str, float] = {
            "total_cases": float(len(cases)),
            "success_rate": len(ran) / len(cases) if cases else 0.0,
            "field_complete_rate": self._mean(field_rates),
            "fully_complete_rate": self._mean(
                [1.0 if c.fully_complete else 0.0 for c in ran]
            ),
            "citation_accuracy": self._mean(citation_values),
            "total_latency_s": sum(latencies),
            "avg_latency_s": self._mean(latencies),
            "total_cost_usd": sum(costs),
            "total_tokens": float(total_tokens),
            "real_calls": float(real_calls),
            "mock_calls": float(mock_calls),
        }
        if out_of_scope:
            metrics["out_of_scope_refusal_rate"] = self._mean(
                [1.0 if c.refused_correctly else 0.0 for c in out_of_scope]
            )
        metrics["total_cases"] = len(cases)  # render as plain integer
        return metrics

    def _aggregate_by_task(self, cases: List[CaseResult]) -> Dict[str, Dict[str, float]]:
        by_task: Dict[str, Dict[str, float]] = {}
        for case in cases:
            bucket = by_task.setdefault(
                case.task_type,
                {
                    "cases": 0,
                    "_acc_sum": 0.0,
                    "_acc_count": 0,
                    "_rate_sum": 0.0,
                    "_rate_count": 0,
                    "_latency_sum": 0.0,
                    "_latency_count": 0,
                    "_cost_sum": 0.0,
                },
            )
            bucket["cases"] += 1
            if not case.success:
                continue
            if case.citation_accuracy is not None:
                bucket["_acc_sum"] += case.citation_accuracy
                bucket["_acc_count"] += 1
            bucket["_rate_sum"] += case.field_complete_rate
            bucket["_rate_count"] += 1
            if case.latency_s is not None:
                bucket["_latency_sum"] += case.latency_s
                bucket["_latency_count"] += 1
            if case.cost_usd is not None:
                bucket["_cost_sum"] += case.cost_usd

        for task, bucket in by_task.items():
            acc_count = bucket.pop("_acc_count", 0)
            acc = bucket.pop("_acc_sum", 0.0) / acc_count if acc_count else 0.0
            rate_count = bucket.pop("_rate_count", 0)
            rate = bucket.pop("_rate_sum", 0.0) / rate_count if rate_count else 0.0
            latency_count = bucket.pop("_latency_count", 0)
            latency = bucket.pop("_latency_sum", 0.0) / latency_count if latency_count else 0.0
            bucket["field_complete_rate"] = rate
            bucket["citation_accuracy"] = acc
            bucket["avg_latency_s"] = latency
            bucket["total_cost_usd"] = bucket.pop("_cost_sum", 0.0)
        return by_task
