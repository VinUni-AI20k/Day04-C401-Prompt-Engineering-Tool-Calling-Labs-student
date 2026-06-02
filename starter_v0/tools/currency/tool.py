from __future__ import annotations

def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Chuyển đổi tiền tệ giả lập."""
    # Mock conversion rates to USD
    rates = {
        "USD": 1.0,
        "EUR": 0.9,
        "VND": 25000.0,
        "JPY": 150.0
    }
    
    from_c = from_currency.upper()
    to_c = to_currency.upper()
    
    if from_c not in rates or to_c not in rates:
        return {
            "items": [],
            "error": f"Loại tiền tệ không được hỗ trợ. Hỗ trợ: {', '.join(rates.keys())}"
        }
    
    amount_in_usd = float(amount) / rates[from_c]
    converted_amount = amount_in_usd * rates[to_c]
    
    return {
        "items": [
            {
                "from": from_c,
                "to": to_c,
                "original_amount": amount,
                "converted_amount": round(converted_amount, 2),
                "summary": f"{amount} {from_c} bằng khoảng {round(converted_amount, 2)} {to_c}"
            }
        ]
    }
