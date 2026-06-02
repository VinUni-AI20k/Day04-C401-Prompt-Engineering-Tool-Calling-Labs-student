---
name: calculator
track: extension
kind: local
requires_env: []
inputs: [expression]
outputs: [expression, result]
side_effect: false
---
# calculator

Safely evaluates mathematical expressions (only basic operators `+`, `-`, `*`, `/`, `.`, parentheses, and numbers are allowed).
