from __future__ import annotations

import json
import os
from typing import Any

from providers.base import ModelResponse, ToolCall
from providers.openai_provider import OpenAIProvider


class OpenCodeProvider(OpenAIProvider):
    """OpenCode Zen gateway — OpenAI-compatible Chat Completions surface."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="OPENCODE_API_KEY",
            base_url=os.getenv("OPENCODE_BASE_URL", "https://opencode.ai/zen/go/v1"),
            default_model="deepseek-v4-flash",
        )

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install live provider dependency first: pip install openai") from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        client = OpenAI(api_key=api_key, base_url=self.base_url)
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "extra_body": {"thinking": {"type": "disabled"}},
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        resp = client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        calls: list[ToolCall] = []
        for call in msg.tool_calls or []:
            args = json.loads(call.function.arguments or "{}")
            calls.append(ToolCall(name=call.function.name, args=args))
        return ModelResponse(text=msg.content, tool_calls=calls, raw=resp)
