from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _telegram_error(response: requests.Response) -> str:
    try:
        data = response.json()
        description = data.get("description")
        if description:
            return str(description)
    except Exception:
        pass
    return f"Telegram API returned HTTP {response.status_code}"


def send_telegram(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    if not confirmed:
        return {
            "tool": "send_telegram",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=TIMEOUT,
        )
        if not response.ok:
            raise RuntimeError(_telegram_error(response))
        return {"tool": "send_telegram", "status": "sent"}
    except Exception as exc:
        return err("send_telegram", exc)
