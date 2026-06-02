from __future__ import annotations

from typing import Any
import requests
from tools._shared import TIMEOUT, err

def convert_currency(amount: float = 1.0, from_currency: str = "USD", to_currency: str = "VND") -> dict[str, Any]:
    from_currency = from_currency.strip().upper()
    to_currency = to_currency.strip().upper()
    try:
        response = requests.get(
            f"https://open.er-api.com/v6/latest/{from_currency}",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        rates = data.get("rates", {})
        rate = rates.get(to_currency)
        if not rate:
            return {"tool": "currency_converter", "error": "InvalidCurrency", "message": f"Target currency {to_currency} not found."}
            
        result = amount * rate
        return {
            "tool": "currency_converter",
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "rate": rate,
            "result": result,
            "last_update": data.get("time_last_update_utc")
        }
    except Exception as exc:
        return err("currency_converter", exc)
