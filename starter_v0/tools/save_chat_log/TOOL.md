# Save Chat Log Tool

Lưu nội dung hội thoại vào file JSON để tham khảo sau này.

## Cách dùng

| Tham số | Loại | Mô tả |
| :--- | :--- | :--- |
| `messages` | list | Danh sách các tin nhắn (role và content). |
| `filename` | string | (Tùy chọn) Tên file muốn lưu. |

```python
from tools.save_chat_log.tool import save_chat_log
result = save_chat_log(messages=[{"role": "user", "content": "hi"}], filename="my_chat.json")
```

## Kết quả trả về

Trả về đường dẫn file đã lưu.
