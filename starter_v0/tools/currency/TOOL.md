---
name: currency
track: core
kind: action
provider: Mock
requires_env: []
inputs: [amount, from_currency, to_currency]
outputs: [items]
side_effect: false
---

## Mô tả
Chuyển đổi tiền tệ giữa các loại tiền tệ phổ biến (mock data).

## Notes
Tool này sử dụng tỷ giá giả lập (mock) để chuyển đổi các loại tiền tệ phổ biến như USD, EUR, VND, JPY.
