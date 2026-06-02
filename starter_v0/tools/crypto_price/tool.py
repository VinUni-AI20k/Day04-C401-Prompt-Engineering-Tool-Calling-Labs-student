from typing import Any, Dict

def get_crypto_price(coin_id: str = "bitcoin") -> Dict[str, Any]:
    """
    Mock hàm lấy giá crypto (có thể thay bằng request lên CoinGecko API)
    """
    # Một bộ dữ liệu giả lập (mock data)
    mock_prices = {
        "bitcoin": 65000.0,
        "ethereum": 3500.0,
        "solana": 140.0,
        "dogecoin": 0.15
    }
    
    coin = coin_id.lower().strip()
    
    if coin in mock_prices:
        return {
            "coin_id": coin,
            "price_usd": mock_prices[coin],
            "status": "success"
        }
    else:
        # Nếu không có trong mock, trả về một giá ngẫu nhiên giả lập hoặc báo lỗi
        return {
            "coin_id": coin,
            "error": "not_found",
            "message": f"Không tìm thấy dữ liệu giá cho đồng {coin_id}."
        }
