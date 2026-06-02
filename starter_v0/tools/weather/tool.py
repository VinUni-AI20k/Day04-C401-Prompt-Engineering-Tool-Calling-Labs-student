from __future__ import annotations
import random

def get_weather(location: str) -> dict:
    """Lấy thông tin thời tiết cho một địa điểm."""
    # Mock data
    conditions = ["Nắng", "Mưa", "Nhiều mây", "Có tuyết", "Gió to"]
    temp = random.randint(15, 35)
    condition = random.choice(conditions)
    
    return {
        "items": [
            {
                "location": location,
                "temperature": f"{temp}°C",
                "condition": condition,
                "summary": f"Thời tiết tại {location} hiện tại là {condition}, nhiệt độ khoảng {temp}°C."
            }
        ]
    }
