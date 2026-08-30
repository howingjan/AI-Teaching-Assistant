"""
Cost and latency monitoring (Phase 4).

Tracks per-generation usage across the pipeline so that every teaching task
records:

  - latency (seconds)
  - estimated prompt / completion tokens
  - estimated cost (USD) using configurable per-1M-token prices
  - mode: "real" (API key configured) or "mock" (offline demo)

Records are appended to logs/usage.jsonl (never containing secrets) and can be
aggregated into the evaluation report.

Prices default to DeepSeek's public per-1M-token rates for deepseek-chat and
can be overridden with environment variables:

  LLM_PRICE_INPUT_PER_M   e.g. "0.27"
  LLM_PRICE_OUTPUT_PER_M  e.g. "1.10"
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.config import Config

logger = logging.getLogger(__name__)

# Rough token estimate: for mixed Chinese/English text ~1.5 chars/token is a
# reasonable approximation used throughout the project (see TextChunker).
CHARS_PER_TOKEN = 1.5

DEFAULT_PRICE_INPUT_PER_M = 0.27   # USD per 1M prompt tokens (deepseek-chat)
DEFAULT_PRICE_OUTPUT_PER_M = 1.10  # USD per 1M completion tokens


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


@dataclass
class CallRecord:
    """A single LLM generation call's usage snapshot."""
    timestamp: str
    task: str
    model: str
    mode: str  # "real" | "mock"
    latency_s: float
    prompt_chars: int = 0
    completion_chars: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def latency_ms(self) -> float:
        return self.latency_s * 1000.0


@dataclass
class UsageSummary:
    """Aggregated usage across a set of call records."""
    calls: int = 0
    real_calls: int = 0
    mock_calls: int = 0
    total_latency_s: float = 0.0
    avg_latency_s: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class UsageMonitor:
    """
    Records, persists and aggregates LLM usage for cost & latency monitoring.

    Thread-safety is not required: the Streamlit app and the demo scripts run
    generation sequentially, one call per task.

    Args:
        persist_path: Path of the append-only JSONL log. Defaults to
            logs/usage.jsonl. Set to None to disable persistence.
    """

    def __init__(
        self,
        persist_path: Optional[Path] = None,
        price_input_per_m: Optional[float] = None,
        price_output_per_m: Optional[float] = None,
    ):
        self.price_input_per_m = (
            price_input_per_m
            if price_input_per_m is not None
            else _env_float("LLM_PRICE_INPUT_PER_M", DEFAULT_PRICE_INPUT_PER_M)
        )
        self.price_output_per_m = (
            price_output_per_m
            if price_output_per_m is not None
            else _env_float("LLM_PRICE_OUTPUT_PER_M", DEFAULT_PRICE_OUTPUT_PER_M)
        )
        if persist_path is None:
            # Default: logs/usage.jsonl (append-only, never contains secrets).
            persist_path = Config.LOGS_DIR / "usage.jsonl"
        self.persist_path = Path(persist_path)
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        self.records: List[CallRecord] = []
        self.last_record: Optional[CallRecord] = None

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return int(len(text or "") / CHARS_PER_TOKEN)

    def record(
        self,
        task: str,
        model: str,
        mode: str,
        latency_s: float,
        prompt_text: str = "",
        completion_text: str = "",
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
    ) -> CallRecord:
        """
        Record a generation call.

        Args:
            task: Teaching task name (lesson, review, ...).
            model: Model identifier in use.
            mode: "real" when an API key is configured, else "mock".
            latency_s: Wall-clock latency of the call in seconds.
            prompt_text: Concatenated prompt content (token estimate source).
            completion_text: Model output (token estimate source).
            prompt_tokens / completion_tokens: Optional exact token counts.
        """
        if prompt_tokens is None:
            prompt_tokens = self._estimate_tokens(prompt_text)
        if completion_tokens is None:
            completion_tokens = self._estimate_tokens(completion_text)

        cost = (
            (prompt_tokens * self.price_input_per_m)
            + (completion_tokens * self.price_output_per_m)
        ) / 1_000_000

        record = CallRecord(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            task=task,
            model=model,
            mode=mode,
            latency_s=round(latency_s, 3),
            prompt_chars=len(prompt_text or ""),
            completion_chars=len(completion_text or ""),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd=round(cost, 6),
        )

        self.records.append(record)
        self.last_record = record
        if self.persist_path is not None:
            self._persist(record)
        return record

    def _persist(self, record: CallRecord) -> None:
        try:
            with open(self.persist_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning(f"Failed to persist usage record: {exc}")

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def aggregate(self, records: Optional[List[CallRecord]] = None) -> UsageSummary:
        """Aggregate usage across the given records (default: all recorded)."""
        items = self.records if records is None else records
        if not items:
            return UsageSummary()

        total_latency = sum(r.latency_s for r in items)
        total_cost = sum(r.cost_usd for r in items)
        total_prompt = sum(r.prompt_tokens for r in items)
        total_completion = sum(r.completion_tokens for r in items)

        return UsageSummary(
            calls=len(items),
            real_calls=sum(1 for r in items if r.mode == "real"),
            mock_calls=sum(1 for r in items if r.mode == "mock"),
            total_latency_s=round(total_latency, 2),
            avg_latency_s=round(total_latency / len(items), 3),
            total_prompt_tokens=total_prompt,
            total_completion_tokens=total_completion,
            total_tokens=total_prompt + total_completion,
            total_cost_usd=round(total_cost, 5),
            avg_cost_usd=round(total_cost / len(items), 6),
        )

    def reset(self) -> None:
        """Clear in-memory records (used between evaluation runs)."""
        self.records.clear()
        self.last_record = None

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def to_markdown(self, records: Optional[List[CallRecord]] = None) -> str:
        """Render a per-call usage table (for evaluation reports)."""
        items = self.records if records is None else records
        if not items:
            return "_（无使用记录）_"

        lines = [
            "| 时间 | 任务 | 模式 | 延迟 (s) | 输入 tokens | 输出 tokens | 成本 (USD) |",
            "|------|------|------|----------|-------------|-------------|------------|",
        ]
        for r in items:
            mode = "真实" if r.mode == "real" else "mock"
            lines.append(
                f"| {r.timestamp} | {r.task} | {mode} | {r.latency_s:.2f} "
                f"| {r.prompt_tokens} | {r.completion_tokens} | {r.cost_usd:.6f} |"
            )
        summary = self.aggregate(items)
        lines.append("")
        lines.append(
            f"合计：{summary.calls} 次调用，总耗时 {summary.total_latency_s:.1f}s "
            f"（平均 {summary.avg_latency_s:.2f}s），"
            f"总 tokens {summary.total_tokens}，预估成本 ${summary.total_cost_usd:.5f}"
        )
        return "\n".join(lines)
