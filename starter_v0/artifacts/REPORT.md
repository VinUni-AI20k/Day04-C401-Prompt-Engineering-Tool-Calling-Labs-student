# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: AI Action Group 2 - Zone 3
- Members: Vũ Đình Phượng - 2A202600634 | Nguyễn Hoàng Dương - 2A202600849
- Provider/model: OpenRouter (openai/gpt-4o-mini)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tra cứu thông tin học thuật, tin tức thời sự trên web/mạng xã hội, đọc liên kết, tự động định dạng báo cáo markdown và gửi tin nhắn Telegram.

**Các điểm nhấn công nghệ và tính năng vượt trội:**
1. **Giao diện Web UI (Playpen) Hiện Đại**: Thiết kế Glassmorphism chuyên nghiệp, hiển thị trực quan các lượt gọi tool và suy nghĩ bên trong của model (Inner Dialogues) dưới dạng hộp thoại thả xuống (collapsible card).
2. **Cơ chế Dừng Agent Khẩn Cấp (Stop Button)**: Nút `🛑 Stop Agent` cho phép ngắt các tác vụ đang chạy lâu hoặc API bị nghẽn mà không làm tắt máy chủ Streamlit.
3. **Luồng Huỷ Thao Tác Tức Thì (Instant Cancel Flow)**: Nút Hủy (`Cancel`) ở hộp xác nhận gửi Telegram hoặc làm rõ thông tin (`clarify`) sẽ phản hồi và đưa người dùng trở lại khung chat ngay lập tức, bỏ qua việc gọi model để tránh trễ.
4. **Phân loại Ý định Thông Minh (Smart Intent Classification)**: Tự động phân tích câu hỏi để quyết định có hiện popup gửi Telegram hay không (Ví dụ: dịch *"I love Vietnam"* thì không hiện popup, nhưng nếu có thêm *"tôi muốn gửi vào Telegram"* thì popup xác nhận mới xuất hiện).
5. **Hỗ trợ 4 Tool Mới**: `current_time` (lấy thời gian hệ thống), `calculator` (tính toán toán học), `dictionary` (tra từ điển tiếng Anh) và `currency_converter` (chuyển tỷ giá thời gian thực).

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://major-gratis-medicines-kirk.trycloudflare.com

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin (có giao diện nút bấm tương tác) | không |
| timeline | lấy các bài viết gần đây của người dùng trên MXH | không |
| social_search | tìm kiếm bài viết MXH theo từ khóa | không |
| lookup | tra cứu tin tức & thông tin trên Internet | không |
| fetch | đọc nội dung thô từ URL liên kết | không |
| format | định dạng dữ liệu tổng hợp thành báo cáo hoàn chỉnh | không |
| send | gửi tin nhắn Telegram (kèm popup xác nhận trên UI) | không (bonus) |
| policy | tra cứu tài liệu quy định nội bộ công ty | không (bonus) |
| papers | tìm kiếm bài báo khoa học trên hệ thống arXiv | không (bonus) |
| paper_text | tải và đọc văn bản của bài báo khoa học arXiv | không (bonus) |
| current_time | lấy ngày giờ hệ thống hiện tại để giải quyết mốc thời gian tương đối | có |
| calculator | tính toán nhanh các biểu thức toán học cơ bản | có |
| dictionary | tra nghĩa từ tiếng Anh trực tuyến | có |
| currency_converter | chuyển đổi tỷ giá tiền tệ trực tiếp | có |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. "Tin tức AI hôm nay có gì nổi bật?" (Tự động tra cứu web và định dạng báo cáo)
2. "Tìm paper arXiv về Retrieval Augmented Generation và lưu lại"
3. "Đổi 500 USD sang VND" (Gọi tool currency_converter)
4. "Tính biểu thức 45 * (12 + 88) / 10" (Gọi tool calculator)
5. "Gửi tin nhắn 'Xin chào' lên Telegram" (Trực tiếp hiển thị dialog xác nhận/hủy thông minh)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Initial version | | 0.70 | runs/v0_B_base_openrouter_20260602T143336991647.json |
| v1 | system_prompt | Define scope & Math/Coding refusal | 0.70 | 0.80 | runs/v1_B_base_openrouter_20260602T144653762294.json |
| v2 | system_prompt | Mapping screenname & single tool per turn | 0.80 | 0.80 | runs/v2_B_base_openrouter_20260602T145100467309.json |
| v3 | system_prompt | Plan & Execute sequence + Parallel search | 0.80 | 0.95 | runs/v3_B_base_openrouter_20260602T153125186988.json |
| v4 | twitter_trends | Add Creative Tool: Twitter Trends | 1.00 | 1.00 | runs/v4_B_group_openrouter_20260602T163459479420.json |

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | lookup | Agent attempted to search for calculus help on web instead of refusing. | Added "Out of Scope" instructions to system_prompt to refuse Math/Coding. |
| R12_confirm_before_send | wrong_boundary | clarify (response_type: "text") | Agent asked for content but used response_type: "text" instead of "yes_no" for confirmation. | Enhanced system_prompt to enforce "yes_no" for tool confirmation flows. |

## B3. Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| T01_trends | Discovery of trending topics on X | twitter_trends | PASS |
| T02_trends_and_lookup | Multi-task: Trends + Web search | twitter_trends + lookup | PASS |
| T03_save_log | Saving chat log with filename | save_chat_log | PASS |
| T04_out_of_scope_joke | Refusal for creative writing | no_tool (refuse) | PASS |
| T05_missing_info_trends | Tool trends without args | twitter_trends | PASS |
| M07_trends_to_lookup | Multi-turn: Trends -> Lookup | lookup | PASS |
| M08_confirm_send_then_save | Multi-turn: Send -> Save log | save_chat_log | PASS |
| M09_clarify_topic_lookup | Multi-turn: Building lookup args | lookup | PASS |
| M10_switch_person_timeline | Multi-turn: Switch person on X | timeline | PASS |
| M11_save_log_with_context | Multi-turn: Save log after turns | save_chat_log | PASS |

## B4. Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "cho tôi biết trend đang hot trên X" | twitter_trends | v4 | Trả về danh sách top trends (Pride Month, Solana, Trump...). |
| 2 | "gửi danh sách nào lên Telegram" | clarify (yes_no) | v3 | Agent hỏi xác nhận trước khi gửi. |
| 4 | "Có, hãy gửi đi" | send (confirmed: true) | v3 | Gửi thành công lên Telegram. |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | .env (TELEGRAM_CHAT_ID) | Gửi tin nhắn thành công qua bot. | Phải qua bước clarify (yes_no) và popup UI xác nhận. |
| arXiv/company policy | tools.yaml | Tra cứu policy và paper khoa học chính xác. | Chỉ tra cứu, không chỉnh sửa nội dung. |
| UI | ui.py | Hiển thị Inner Dialogue, Stop Button, và Chat History Sidebar. | Ngắt stream khi bấm Stop để tránh treo session. |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`? Logic từ chối (Math/Coding), quy trình xác nhận (yes_no), mapping screenname (sama, elonmusk).
- Which fixes belonged in `tools.yaml`? Thêm tool mới (twitter_trends, save_chat_log), cập nhật mô tả tham số để model gọi chính xác hơn.
- Which failure needed manual review instead of automatic grading? Các case liên quan đến "nuance" trong câu trả lời văn bản (actual_text) mà eval chỉ check tool_calls.
- What would you improve next? Thêm tính năng nhớ ngữ cảnh dài hạn (memory) và hỗ trợ đa ngôn ngữ tốt hơn trong các báo cáo format.
