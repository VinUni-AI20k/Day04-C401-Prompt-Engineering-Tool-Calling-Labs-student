# Báo Cáo Demo Day 04 Lab v2 - Research Agent

## Nhóm

- Team:
- Members:
- Provider/model: gemini / gemini-3.1-flash-lite

## Metrics Hiện Tại

Bản demo report này mới ghi lại kết quả đã chạy của `v0` và `v1`. Các phần `v2`, `v3`, group eval và chat transcript vẫn cần làm tiếp.

| Version | Run File | Artifact Version | Case Được Đo | Provider Error | Case Accuracy | Tool Routing Accuracy | Argument Accuracy | Multiturn Accuracy |
|---|---|---|---:|---:|---:|---:|---:|---:|
| v0 | runs/v0_B_base_gemini_20260602T123816407145.json | v0+pf0c107a9d7a1+t011c271ef0bb | 16/20 | 4 | 0.5625 | 0.75 | 0.5625 | 0.5 |
| v1 | runs/v1_B_base_gemini_20260602T134746673233.json | v1+pd745c44513e8+t011c271ef0bb | 18/20 | 2 | 0.8333 | 1.0 | 0.8333 | 1.0 |

Ghi chú: các lỗi `provider_error` là do Gemini free-tier bị rate limit, không phải do lỗi chọn tool của agent.

## Evidence Theo Version

| Version | Artifact Đã Sửa | Giả Thuyết | Metric Trước | Metric Sau | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi repo mẫu trước khi sửa prompt hoặc tool declaration. |  | 0.5625 | runs/v0_B_base_gemini_20260602T123816407145.json |
| v1 | system_prompt.md | Nếu prompt có rule rõ về clarify, confirmation, scope, parallel tool use và argument conventions thì model sẽ ít đoán bừa và ít sai boundary hơn. | 0.5625 | 0.8333 | runs/v1_B_base_gemini_20260602T134746673233.json |

## Phân Tích Lỗi v0

| Case ID | Failure Type | Tool Call Thực Tế | Lỗi Gì | Fix Trong v1 |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool / wrong_arg_value | lookup(query="AI news today", topic="news") | Model chọn đúng tool nhưng đưa cả từ chỉ thời gian/news vào `query` và thiếu `timeframe=day`. | Thêm quy ước argument: `query` chỉ giữ chủ đề sạch, "hôm nay" map sang `timeframe=day`. |
| R08_out_of_scope | out_of_scope | send(text="Nguyên hàm của x^2...") | Model gọi tool cho câu hỏi toán, trong khi câu này nằm ngoài scope research agent. | Thêm scope boundary: không gọi tool cho toán, coding hoặc câu hỏi meta. |
| R10_missing_handle | missing_info | timeline(screenname="sama", limit=5) | Model đoán Sam Altman dù user chưa cung cấp account. | Thêm rule: thiếu account/person cho tweet thì gọi `clarify` với `response_type=text`. |
| R11_missing_url | missing_info | lookup(query="tóm tắt bài viết mới nhất về công nghệ AI") | Model tự đoán topic thay vì hỏi URL bị thiếu. | Thêm rule: nói "bài này/this article" mà không có URL thì gọi `clarify` với `response_type=text`. |
| R12_confirm_before_send | wrong_boundary | send(text="Bản tin mới nhất...") | Model thử gửi nội dung khi chưa có xác nhận rõ ràng từ user. | Thêm rule: send/post/publish phải hỏi xác nhận `clarify response_type=yes_no` trước khi gọi `send`. |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | lookup(query="AI news today", topic="news", timeframe="day"); social_search(query="AI", search_type="Latest") | Model gọi đúng cả hai tool nhưng `query` của lookup vẫn bị mở rộng quá mức. | Thêm quy ước query sạch, không nhét "news/today" vào query. |
| M06_switch_tool | wrong_tool / wrong_arg_value | lookup(query="OpenAI news", topic="news", timeframe="week") | Model đã chuyển sang đúng tool nhưng vẫn thêm "news" vào `query`. | Thêm rule cho multi-turn và query-cleaning. |

## Lỗi Còn Lại Ở v1

| Case ID | Failure Type | Tool Call Thực Tế | Lỗi Gì | Fix Tiếp Theo |
|---|---|---|---|---|
| R10_missing_handle | missing_info | clarify(question="Bạn muốn xem 5 tweet mới nhất của tài khoản nào?") | Model đã dùng `clarify` nhưng thiếu `response_type="text"`. | Cần sửa tool declaration của `clarify` để nhấn mạnh phải set rõ `response_type`. |
| R11_missing_url | missing_info | clarify(question="Bạn vui lòng cung cấp đường dẫn...") | Model đã dùng `clarify` nhưng thiếu `response_type="text"`. | Cần sửa tool declaration của `clarify` để nhấn mạnh phải set rõ `response_type`. |
| R12_confirm_before_send | wrong_boundary | clarify(question="Bạn vui lòng cung cấp nội dung bản tin...") | Model đã dùng `clarify` nhưng thiếu `response_type="yes_no"` và hỏi nội dung thay vì hỏi xác nhận. | Cần sửa declaration của `send`/`clarify` để làm rõ confirmation boundary và `response_type=yes_no`. |

## Việc Cần Làm Tiếp

- v2: sửa `artifacts/tools.yaml` dựa trên lỗi còn lại của v1.
- v3: chạy thêm một vòng tối ưu cuối sau v2.
- `data/eval_group.json`: thêm 10 case của nhóm, gồm 5 single-turn và 5 multi-turn.
- Thêm ít nhất 1 tool mới, có `TOOL.md`, `tool.py`, registry entry trong `tools/__init__.py`, khai báo trong `tools.yaml`, và case group eval kiểm tra tool đó.
- Chạy group eval bằng version v3.
- Chạy `chat.py` bằng version v3 và lưu transcript evidence.
- Điền `REPORT.md` chính thức bằng log thật từ v2/v3/group/chat.

