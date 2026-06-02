---
name: summarize
track: core
kind: local_formatter
requires_env: []
inputs: [text, max_sentences, max_chars]
outputs: [summary, original_length, summary_length]
side_effect: false
---
# summarize

Tóm tắt văn bản dài thành ngắn bằng cách trích xuất các câu quan trọng.

- `text`: Văn bản cần tóm tắt (bắt buộc).
- `max_sentences`: Số câu tối đa trong bản tóm tắt (mặc định 5).
- `max_chars`: Số ký tự tối đa trong bản tóm tắt (mặc định 500). Nếu cả hai tham số đều được đặt, `max_chars` được ưu tiên.
