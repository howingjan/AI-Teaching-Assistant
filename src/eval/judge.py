"""LLM-as-judge scoring for generated answers (optional, requires an API key).

The judge uses the configured LLM to score two orthogonal dimensions:

  - faithfulness: is every claim in the answer supported by the retrieved context?
  - answer relevance: does the answer directly address the question?

Scores are 1-5 with a short rationale, returned as JSON so they can be
aggregated into regression reports. This module is deliberately decoupled from
retrieval metrics so it can be run selectively when an API key is available.
"""

import logging
from typing import Any, Dict, Optional

from src.rag.llm_client import LLMClient, parse_json_response

logger = logging.getLogger(__name__)

_FAITHFULNESS_PROMPT = (
    "你是严谨的评估裁判。判断以下「答案」中的每一条陈述是否都能由「参考资料」支持，"
    "或只是合理常识推断。仅依据忠实度打分，不评价语言流畅度。"
    "返回 JSON 对象：{\"score\": 1-5 的整数, \"rationale\": \"一句话中文理由\"}。"
)
_RELEVANCE_PROMPT = (
    "你是严谨的评估裁判。判断以下「答案」是否直接、完整地回答了「问题」，"
    "没有答非所问或遗漏关键部分。返回 JSON 对象："
    "{\"score\": 1-5 的整数, \"rationale\": \"一句话中文理由\"}。"
)


class LLMJudge:
    """Score generated answers with an LLM, for offline regression evaluation."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        if not self.llm.available:
            raise RuntimeError(
                "LLM-as-judge 需要配置 LLM API key（DEEPSEEK_API_KEY 等），无法离线运行。"
            )

    def _score(self, system: str, user: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        raw = self.llm.generate(messages, json_mode=True, temperature=0.0)
        data = parse_json_response(raw)
        try:
            score = int(data.get("score", 0))
        except (TypeError, ValueError):
            score = 0
        return {
            "score": max(1, min(5, score)),
            "rationale": str(data.get("rationale", "")).strip(),
        }

    def evaluate_faithfulness(self, answer: str, context: str) -> Dict[str, Any]:
        """Score whether the answer is supported by the provided context."""
        return self._score(
            _FAITHFULNESS_PROMPT,
            f"参考资料：\n{context}\n\n答案：\n{answer}",
        )

    def evaluate_answer_relevance(self, question: str, answer: str) -> Dict[str, Any]:
        """Score whether the answer directly addresses the question."""
        return self._score(
            _RELEVANCE_PROMPT,
            f"问题：\n{question}\n\n答案：\n{answer}",
        )
