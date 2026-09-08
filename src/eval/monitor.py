"""Cost / latency usage recording.

Every generation call records latency, estimated prompt/completion tokens and
estimated cost (USD, DeepSeek per-1M-token prices, overridable via env). The
Streamlit UI displays the latest record; records may optionally be appended to
logs/usage.jsonl (never containing secrets).
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.core.config import Config

logger = logging.getLogger(__name__)

# Rough estimate: mixed Chinese/English ~1.5 chars per token.
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
    mode: str = "real"
    latency_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class UsageMonitor:
    """Records LLM usage for cost / latency display and optional logging."""

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
            persist_path = Config.LOGS_DIR / "usage.jsonl"
        self.persist_path = Path(persist_path)
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        self.records: List[CallRecord] = []
        self.last_record: Optional[CallRecord] = None

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return int(len(text or "") / CHARS_PER_TOKEN)

    def record(
        self,
        task: str,
        model: str,
        mode: str = "real",
        latency_s: float = 0.0,
        prompt_text: str = "",
        completion_text: str = "",
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
    ) -> CallRecord:
        """Record one generation call."""
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

    def reset(self) -> None:
        """Clear in-memory records."""
        self.records.clear()
        self.last_record = None

    def _persist(self, record: CallRecord) -> None:
        try:
            with open(self.persist_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning(f"Failed to persist usage record: {exc}")
