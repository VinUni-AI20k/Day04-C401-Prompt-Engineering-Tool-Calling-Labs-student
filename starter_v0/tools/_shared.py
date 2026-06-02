from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}


def sanitize_tool_output(text: str) -> str:
    if not text:
        return ""
    # 1. Neutralize common instruction-spoofing / jailbreak phrases
    injection_patterns = [
        (r"(?i)\bignore\s+(?:all\s+)?(?:previous\s+)?instructions?\b", "[REMOVED_BYPASS_ATTEMPT]"),
        (r"(?i)\bforget\s+(?:all\s+)?rules?\b", "[REMOVED_BYPASS_ATTEMPT]"),
        (r"(?i)\bsystem\s+prompts?\b", "[REMOVED_SENSITIVE_TERM]"),
        (r"(?i)\byou\s+are\s+now\s+a\b", "[REMOVED_ROLE_PLAY]"),
        (r"(?i)\bnew\s+instructions?\b", "[REMOVED_INSTRUCTION_TERM]"),
    ]
    sanitized = text
    for pattern, replacement in injection_patterns:
        sanitized = re.sub(pattern, replacement, sanitized)
    
    # 2. Escape system-like role tags in brackets to prevent LLM chat boundary confusion
    role_patterns = [
        (r"(?i)\[system\]", "\\[system\\]"),
        (r"(?i)\[assistant\]", "\\[assistant\\]"),
        (r"(?i)\[user\]", "\\[user\\]"),
        (r"(?i)\[instruction\]", "\\[instruction\\]"),
        (r"(?i)\[developer\]", "\\[developer\\]"),
        (r"(?i)<system>", "&lt;system&gt;"),
        (r"(?i)<assistant>", "&lt;assistant&gt;"),
        (r"(?i)<user>", "&lt;user&gt;"),
        (r"(?i)<instruction>", "&lt;instruction&gt;"),
        (r"(?i)<developer>", "&lt;developer&gt;"),
    ]
    for pattern, replacement in role_patterns:
        sanitized = re.sub(pattern, replacement, sanitized)
        
    return sanitized


