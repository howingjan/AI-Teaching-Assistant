"""
LLM client wrapper (Phase 2).

Wraps the DeepSeek chat-completions API (OpenAI-compatible) behind a simple
interface:

    client = LLMClient()
    raw = client.generate(messages, json_mode=True)
    data = parse_json_response(raw)

When no API key is configured, LLMClient falls back to an offline MOCK mode
that returns deterministic structured JSON, so the full pipeline can be
demonstrated and tested without network access.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from src.core.config import Config

logger = logging.getLogger(__name__)


def parse_json_response(raw: str) -> Dict[str, Any]:
    """
    Parse a JSON object out of an LLM response.

    Handles:
      - plain JSON:  {"a": 1}
      - fenced:      ```json ... ```
      - prose-wrapped: "Here is the result: {...} thanks"

    Args:
        raw: Raw model output string.

    Returns:
        Parsed dict.

    Raises:
        ValueError: if no valid JSON object can be extracted.
    """
    if raw is None:
        return {}

    text = str(raw).strip()
    if not text:
        return {}

    # Strip markdown code fences (json or plain).
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text).strip()

    # Extract the first balanced {...} region if surrounded by prose.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON object found in model output: {raw[:200]!r}")

    candidate = text[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model output is not valid JSON: {candidate[:200]!r}") from exc


class LLMClient:
    """
    Thin wrapper around a chat-completions endpoint (default: DeepSeek).

    Attributes:
        available: True when an API key is configured and generation can run.
        model: The model identifier in use.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.api_key = api_key if api_key is not None else Config.DEEPSEEK_API_KEY
        self.model = model or Config.llm.model
        self.temperature = temperature if temperature is not None else Config.llm.temperature
        self.max_tokens = max_tokens or Config.llm.max_tokens
        self.api_base_url = Config.llm.api_base_url
        self.timeout = Config.llm.timeout_seconds
        self.retry_count = Config.llm.retry_count

        # Empty string means "no key" (tests rely on this).
        self.available = bool(self.api_key) and self.api_key != "your_api_key_here"

        self._client = None
        if self.available:
            self._client = self._build_client()

    # ------------------------------------------------------------------
    # Client construction
    # ------------------------------------------------------------------

    def _build_client(self):
        """Create the OpenAI-compatible client object (lazy import)."""
        try:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key, base_url=self.api_base_url)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"Failed to build OpenAI client: {exc}")
            self.available = False
            return None

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        messages: List[dict],
        json_mode: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """
        Generate a completion for a list of chat messages.

        Args:
            messages: Chat messages ([{"role": ..., "content": ...}, ...]).
            json_mode: When True, request a JSON-object response and post-process.
            temperature: Override temperature for this call.
            max_tokens: Override max tokens for this call.

        Returns:
            Raw model output text.
        """
        if not self.available or self._client is None:
            return self._mock_generate(messages, json_mode=json_mode)

        return self._api_generate(
            messages,
            json_mode=json_mode,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _api_generate(
        self,
        messages: List[dict],
        json_mode: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Call the chat-completions API with retries."""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "timeout": self.timeout,
        }
        if json_mode:
            # DeepSeek supports response_format json_object.
            kwargs["response_format"] = {"type": "json_object"}

        last_exc = None
        for attempt in range(self.retry_count):
            try:
                resp = self._client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content or ""
            except Exception as exc:
                last_exc = exc
                logger.warning(f"LLM API attempt {attempt + 1} failed: {exc}")
        raise RuntimeError(f"LLM API failed after {self.retry_count} attempts: {last_exc}")

    # ------------------------------------------------------------------
    # Mock mode
    # ------------------------------------------------------------------

    def _mock_generate(self, messages: List[dict], json_mode: bool = False) -> str:
        """
        Deterministic offline generator for demos/tests.

        Extracts the lesson topic from the user message (【本周主题】...) and
        returns a complete, clearly-marked mock lesson JSON.
        """
        user_content = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_content += str(msg.get("content", "")) + "\n"

        topic = "（未指定）"
        match = re.search(r"【本周主题】([^\n【】]+)", user_content)
        if match:
            topic = match.group(1).strip()

        # Also try the problem/review/cheatsheet entry points for nicer demos.
        if topic == "（未指定）":
            for pattern in (r"【题目】([^\n【】]+)", r"【复习范围】([^\n【】]+)", r"【考试范围】([^\n【】]+)"):
                m = re.search(pattern, user_content)
                if m:
                    topic = m.group(1).strip()
                    break

        payload = {
            "task_type": "lesson",
            "topic": topic,
            "learning_objectives": [
                f"理解「{topic}」的核心概念与定义",
                "能够用中文解释相关英文术语",
                "能完成对应的基础练习",
            ],
            "prerequisites": ["课程前期讲解的基础概念", "基本的数据分析思维"],
            "core_explanation": (
                f"（mock 内容）本小节围绕「{topic}」展开。"
                "真实生成模式下，系统会检索课程资料并给出带来源页码的中文讲解。"
            ),
            "terminology": [
                {"term": topic, "explanation": "（mock）术语的中文解释由真实模型生成"}
            ],
            "examples": [
                {"title": "课堂示例", "content": "（mock）此处为简单例子，真实模式下由资料驱动生成"}
            ],
            "misconceptions": ["（mock）常见误区示例，真实模式下依据资料整理"],
            "discussion_questions": [f"你认为「{topic}」在什么场景下最有用？"],
            "exercises": [
                {
                    "question": f"（mock）请用自己的话解释「{topic}」。",
                    "hint": "（mock）提示：从定义和应用场景两个角度回答。",
                    "reference_answer": "（mock）参考答案由真实模型结合资料生成。",
                }
            ],
            "citations": [],
            "needs_review": [
                "当前为 mock 模式（未配置 DEEPSEEK_API_KEY），内容未经真实检索与模型生成，需要老师重新生成。"
            ],
            "insufficient_material": False,
        }
        return json.dumps(payload, ensure_ascii=False)
