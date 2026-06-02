# Crypto Price Tool

Fetch real-time cryptocurrency pricing, 24-hour percentage price changes, and market capitalization statistics.

## Parameters

*   `coin` (string, required): The symbol or name of the cryptocurrency (e.g., `"BTC"`, `"Ethereum"`, `"sol"`, `"dogecoin"`).

## Returns

A JSON object containing:
*   `status`: `"success"` or `"error"`.
*   `coin`: Original query coin.
*   `price_usd`: Current price in US Dollars.
*   `change_24h_percent`: Percentage change in price over the last 24 hours.
*   `market_cap_usd`: Total market capitalization in US Dollars.
*   `data_source`: Live or fallback database indicator.
