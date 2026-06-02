---
name: translate
track: bonus
kind: live_api
provider: MyMemory
requires_env: []
inputs: [text, source_lang, target_lang]
outputs: [translated_text, source_lang, target_lang]
side_effect: false
---
# translate

Translate text between languages using MyMemory API (free, no API key required).
Supports common language codes: en, vi, ja, ko, zh, fr, de, es, etc.
