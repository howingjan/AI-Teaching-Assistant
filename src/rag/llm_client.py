"""
LLM client wrapper (Phase 2).

Wraps the DeepSeek chat-completions API (OpenAI-compatible) behind a simple
interface:

    client = LLMClient()
    raw = client.generate(messages, json_mode=True)
    data = parse_json_response(raw)

No offline/mock fallback is provided: generate() always calls the real model
API, so DEEPSEEK_API_KEY must be configured before any generation call.
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

    # Locate the first '{' and extract the *balanced* {...} object, so any
    # trailing prose (or a stray closing brace) does not corrupt the payload.
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in model output: {raw[:200]!r}")

    depth = 0
    in_string = False
    escaped = False
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise ValueError(f"Unbalanced JSON object in model output: {raw[:200]!r}")

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
        provider: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self.provider = (provider or Config.llm.provider).lower()
        self.api_key = api_key if api_key is not None else self._resolve_api_key()
        self.model = model or self._default_model()
        self.temperature = temperature if temperature is not None else Config.llm.temperature
        self.max_tokens = max_tokens or Config.llm.max_tokens
        self.api_base_url = Config.llm.api_base_url
        self.azure_endpoint = Config.llm.azure_endpoint
        self.azure_api_version = api_version or Config.llm.azure_api_version
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

    def _default_model(self) -> str:
        if self.provider == "azure":
            return Config.llm.azure_deployment or Config.llm.model
        return Config.llm.model

    def _resolve_api_key(self) -> Optional[str]:
        """Resolve the API key for the active provider, with a DeepSeek fallback."""
        if self.provider == "azure":
            return Config.AZURE_OPENAI_API_KEY or Config.DEEPSEEK_API_KEY
        if self.provider == "openai":
            return Config.OPENAI_API_KEY or Config.DEEPSEEK_API_KEY
        return Config.DEEPSEEK_API_KEY

    def _build_client(self):
        """Create the provider-specific OpenAI-compatible client (lazy import)."""
        try:
            if self.provider == "azure":
                from openai import AzureOpenAI
                return AzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.azure_endpoint,
                    api_version=self.azure_api_version,
                )
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
            raise RuntimeError(
                "未配置 DEEPSEEK_API_KEY，无法真实生成。"
                "请在项目根目录 .env 中配置 DEEPSEEK_API_KEY 后重试。"
            )

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
