from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err


MEMORY_DIR = ROOT / "memory_store"
ALLOWED_TYPES = {"user", "feedback", "project", "reference", "note"}


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip().lower()).strip("-._")
    return slug or "memory"


def add_memory(name: str = "", content: str = "", memory_type: str = "note", tags: list[str] | None = None) -> dict[str, Any]:
    try:
        clean_name = name.strip()
        clean_content = content.strip()
        clean_type = (memory_type or "note").strip().lower()
        if not clean_name:
            return {"tool": "add_memory", "status": "error", "message": "name is required"}
        if not clean_content:
            return {"tool": "add_memory", "status": "error", "message": "content is required"}
        if clean_type not in ALLOWED_TYPES:
            return {
                "tool": "add_memory",
                "status": "error",
                "message": f"memory_type must be one of {sorted(ALLOWED_TYPES)}",
            }

        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        path = MEMORY_DIR / f"{_slug(clean_name)}.json"
        record = {
            "name": clean_name,
            "content": clean_content,
            "memory_type": clean_type,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"tool": "add_memory", "status": "saved", "path": str(path), "record": record}
    except Exception as exc:
        return err("add_memory", exc)
