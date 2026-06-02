from __future__ import annotations

from datetime import datetime
from typing import Any

def get_current_time() -> dict[str, Any]:
    now = datetime.now()
    return {
        "tool": "current_time",
        "current_time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "day_of_week": now.strftime("%A"),
        "iso_timestamp": now.isoformat()
    }
