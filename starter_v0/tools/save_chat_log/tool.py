from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from .._shared import err

def save_chat_log(messages: list[dict[str, str]], filename: str | None = None) -> dict[str, Any]:
    """
    Saves the provided chat messages to a log file.
    """
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            filename = f"chat_log_{timestamp}.json"
        
        if not filename.endswith(".json"):
            filename += ".json"
            
        file_path = log_dir / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({
                "saved_at": datetime.now().isoformat(),
                "messages": messages
            }, f, ensure_ascii=False, indent=2)
            
        return {
            "tool": "save_chat_log",
            "status": "success",
            "file_path": str(file_path),
            "message": f"Chat log has been saved to {file_path}"
        }
    except Exception as exc:
        return err("save_chat_log", exc)
