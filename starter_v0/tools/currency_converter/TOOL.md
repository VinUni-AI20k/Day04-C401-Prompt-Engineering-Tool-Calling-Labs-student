---
name: currency_converter
track: extension
kind: live_api
requires_env: []
inputs: [amount, from_currency, to_currency]
outputs: [amount, from, to, rate, result, last_update]
side_effect: false
---
# currency_converter

Converts currency amounts between different international currencies (e.g. USD, VND, EUR) using real-time rates from ER-API.
