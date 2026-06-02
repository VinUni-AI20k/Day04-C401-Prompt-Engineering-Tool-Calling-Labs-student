from __future__ import annotations

import re
from typing import Any

def evaluate_expression(expression: str) -> dict[str, Any]:
    # Sanitize: allow only numbers, basic math operators, spaces, and parenthesis
    cleaned = re.sub(r"[^0-9+\-*/().\s]", "", expression)
    if not cleaned.strip():
        return {"tool": "calculator", "error": "InvalidExpression", "message": "Expression contains invalid characters."}
    try:
        # Evaluate safely in a restricted scope
        res = eval(cleaned, {"__builtins__": None}, {})
        return {"tool": "calculator", "expression": expression, "result": res}
    except Exception as exc:
        return {"tool": "calculator", "error": type(exc).__name__, "message": str(exc)}
