from __future__ import annotations

def calculate(expression: str) -> dict:
    """Thực hiện phép tính toán học dựa trên biểu thức đầu vào."""
    try:
        # Chỉ cho phép các ký tự an toàn
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Biểu thức chứa ký tự không hợp lệ.")
            
        result = eval(expression, {"__builtins__": {}})
        return {
            "items": [
                {
                    "expression": expression,
                    "result": result,
                    "summary": f"Kết quả của {expression} là {result}"
                }
            ]
        }
    except Exception as e:
        return {
            "items": [],
            "error": str(e)
        }
