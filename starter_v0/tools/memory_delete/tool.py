from __future__ import annotations

import re
from typing import Any

from tools._shared import ROOT, err


MEMORY_DIR = ROOT / "memory_store"


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip().lower()).strip("-._")
    return slug or "memory"


def delete_memory(name: str = "") -> dict[str, Any]:
    try:
        clean_name = name.strip()
        if not clean_name:
            return {"tool": "delete_memory", "status": "error", "message": "name is required"}

        path = MEMORY_DIR / f"{_slug(clean_name)}.json"
        if not path.exists():
            return {"tool": "delete_memory", "status": "not_found", "path": str(path)}

        path.unlink()
        return {"tool": "delete_memory", "status": "deleted", "path": str(path)}
    except Exception as exc:
        return err("delete_memory", exc)
