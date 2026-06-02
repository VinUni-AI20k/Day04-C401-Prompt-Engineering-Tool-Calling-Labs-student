from __future__ import annotations

import json
import os
from typing import Any

from providers.base import ModelResponse, ToolCall


SAFE_REFUSAL = (
    "Mình không thể hỗ trợ nội dung liên quan đến bạo lực, vũ khí "
    "hoặc hành vi nguy hiểm. Nếu đây là tình huống thật, hãy báo ngay "
    "cho giáo viên, người lớn đáng tin cậy hoặc cơ quan chức năng."
)


class OpenAIProvider:
    """OpenAI Chat Completions provider with normalized tool_calls output."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.default_model = default_model

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
            from openai import OpenAI, PermissionDeniedError, APIStatusError
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
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        try:
            resp = client.chat.completions.create(**kwargs)
        except PermissionDeniedError as e:
            error_text = str(e).lower()
            if any(x in error_text for x in ["flagged", "moderation", "illicit/violent", "requires moderation"]):
                return ModelResponse(text=SAFE_REFUSAL, tool_calls=[], raw=None)
            return ModelResponse(
                text="Request bị từ chối quyền truy cập. Vui lòng kiểm tra API key hoặc model.",
                tool_calls=[], raw=None,
            )
        except APIStatusError as e:
            if e.status_code == 403:
                return ModelResponse(text=SAFE_REFUSAL, tool_calls=[], raw=None)
            return ModelResponse(text=f"Lỗi API: {e.status_code}", tool_calls=[], raw=None)

        msg = resp.choices[0].message
        calls: list[ToolCall] = []
        for call in msg.tool_calls or []:
            args = json.loads(call.function.arguments or "{}")
            calls.append(ToolCall(name=call.function.name, args=args))
        return ModelResponse(text=msg.content, tool_calls=calls, raw=resp)
