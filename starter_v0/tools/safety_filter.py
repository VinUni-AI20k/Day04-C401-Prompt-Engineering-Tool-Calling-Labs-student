"""
Content Safety Filter for Research Agent.
Blocks dangerous content before sending to model.
"""
from __future__ import annotations

from typing import Any

# Refuse message for dangerous content
SAFE_REFUSAL = (
    "Mình không thể hỗ trợ nội dung liên quan đến bạo lực, vũ khí "
    "hoặc hành vi nguy hiểm. Nếu đây là tình huống thật, hãy báo ngay "
    "cho giáo viên, người lớn đáng tin cậy hoặc cơ quan chức năng."
)

# Keywords that trigger safety block
DANGEROUS_KEYWORDS = [
    "súng",
    "vũ khí",
    "dao",
    "bom",
    "chất nổ",
    "giết",
    "bắn",
    "mang súng vào lớp",
    "mang vũ khí vào trường",
    "tấn công",
    "đe dọa",
    "tự tử",
    "tự hại",
]


def is_dangerous_input(text: str) -> bool:
    """Check if input text contains dangerous keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in DANGEROUS_KEYWORDS)


def check_safety(text: str) -> str | None:
    """
    Check safety of input text.
    Returns SAFE_REFUSAL if dangerous, None if safe.
    """
    if is_dangerous_input(text):
        return SAFE_REFUSAL
    return None


def filter_messages_safety(messages: list[dict[str, str]]) -> tuple[bool, str | None]:
    """
    Check safety for the latest user message.
    Returns (is_safe, refusal_message).
    - If safe: (True, None)
    - If dangerous: (False, SAFE_REFUSAL)
    """
    # Find the last user message
    user_messages = [m for m in messages if m.get("role") == "user"]
    if not user_messages:
        return True, None

    last_user_msg = user_messages[-1].get("content", "")
    refusal = check_safety(last_user_msg)

    if refusal:
        return False, refusal
    return True, None
