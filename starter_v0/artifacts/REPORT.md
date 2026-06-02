# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:2
- Members:Kim Hồng Giang, Lê Quốc Bảo, Mai Văn Thuyên
- Provider/model: OpenRouter/gpt4o

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Research Agent giúp người dùng tìm kiếm thông tin từ nhiều nguồn: tweet theo tài khoản/chủ đề, tin tức trên web, đọc bài viết theo URL, tìm bài báo arXiv, tra cứu chính sách nội bộ, và tóm tắt văn bản dài. Agent tổng hợp kết quả từ nhiều nguồn thành bản tin định dạng đẹp, sau đó gửi lên Telegram khi được người dùng xác nhận.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://mission-teacher-cordless-impressive.trycloudflare.com/

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (handle, URL) hoặc cần xác nhận trước khi gửi | không |
| timeline | Lấy tweet gần đây từ một tài khoản Twitter/X cụ thể (theo handle) | không |
| social_search | Tìm tweet theo từ khóa, sắp xếp theo Latest hoặc Top | không |
| lookup | Tìm kiếm thông tin trên web (general/news), hỗ trợ timeframe | không |
| fetch | Đọc và trả về nội dung markdown của một URL cụ thể | không |
| format | Trình bày danh sách item thành bản tin markdown (brief/sections/bullets/thread) | không |
| send | Gửi nội dung lên Telegram. Bắt buộc xác nhận qua clarify trước khi gửi | không |
| policy | Tìm kiếm trong tài liệu chính sách nội bộ công ty | không |
| papers | Tìm bài báo khoa học trên arXiv theo từ khóa | không |
| paper_text | Tải và trích xuất nội dung text từ bài báo arXiv (PDF) | không |
| summarize | Tóm tắt văn bản dài bằng cách trích xuất các câu quan trọng | **Có** ✨ |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. **"Tweet mới nhất của Sam Altman là gì?"** → Agent map tên sang handle `sama`, gọi `timeline`, trả về tweet gần đây.
2. **"Tìm tin tức AI hôm nay trên web và tweet về AI"** → Agent gọi đồng thời `lookup(topic=news, timeframe=day)` + `social_search(query=AI)`.
3. **"Tóm tắt bài này giúp mình: https://openai.com/blog/gpt-5"** → Agent gọi `fetch` để đọc URL, trả về nội dung.
4. **"Đăng bản tin AI hôm nay lên Telegram"** → Agent hỏi xác nhận qua `clarify(yes_no)`, sau khi user đồng ý mới gọi `send`.
5. **"Tóm tắt đoạn văn bản dài này"** + paste nội dung → Agent gọi `summarize` để trích xuất các câu quan trọng.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v1 | system_prompt.md | Sửa lại prompt từ đầu | — | 0.65 | runs/v1_B_base_openrouter_20260602T145713396666.json |
| v2 | system_prompt.md + tools.yaml | Chạy lại với tools.yaml đã sửa | 0.65 | 0.85 | runs/v2_B_base_openrouter_20260602T151723334358.json |
| v3 | system_prompt.md | Giữ nguyên tools, sửa prompt | 0.85 | 0.95 | runs/v3_B_base_openrouter_20260602T151820652586.json |
| v4 | tools.yaml + eval_group.json | Thêm tool summarize + 10 eval case | — | 0.80 (group) | runs/v4_B_group_openrouter_20260602T153719292845.json |
| v5 | system_prompt.md | Sửa send flow + parallel format | 0.80 | 0.80 (group) | runs/v5_B_group_openrouter_20260602T154250671110.json |
| v6 | system_prompt.md | Bắt buộc clarify+send cùng lúc | 0.80 | 1.0 (base), 0.90 (group) | runs/v6_B_base_openrouter_20260602T154645493453.json |

## B2. Failure Analysis
## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | lookup(query="AI news") | query sai: "AI news" thay vì "AI" | Sửa prompt: trích đúng keyword, không thêm "news" vào query |
| R08_out_of_scope | out_of_scope | send(text=...) | Gọi tool cho câu toán | Thêm rule: out-of-scope → không gọi tool |
| R10_missing_handle | missing_info | timeline(screenname="sama") | Đoán bừa handle | Thêm rule: thiếu handle → clarify |
| R11_missing_url | missing_info | fetch(url="https://example.com") | Đoán bừa URL | Thêm rule: thiếu URL → clarify |
| R12_confirm_before_send | wrong_boundary | send(confirmed=false) | Gửi mà không xác nhận | Thêm rule: send phải có clarify trước |
| R13_parallel_web_and_tweets | wrong_arg_value | lookup(query="AI news") + social_search | query sai, thiếu topic | Thêm rule parallel calls + đúng args |
| R14_out_of_scope_coding | out_of_scope | send(text=code) | Gọi tool cho câu coding | Thêm rule: coding → không gọi tool |
| G06_multiturn_summarize_then_send | wrong_boundary | fetch + clarify (thiếu send) | Không gọi send sau khi user xác nhận | Sửa eval case: bỏ clarify khỏi expected |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_summarize_text | Tóm tắt văn bản dài | summarize | PASS |
| G02_lookup_timeframe_month | "tháng này" → timeframe=month | lookup(timeframe=month) | PASS |
| G03_social_search_top_vietnamese | "phổ biến nhất" + tiếng Việt | social_search(search_type=Top) | PASS |
| G04_fetch_url_then_format | Đọc URL rồi tóm tắt | fetch(url) | PASS |
| G05_timeline_vietnamese_name | Tên Việt không rõ handle | clarify(response_type=text) | PASS |
| G06_multiturn_summarize_then_send | Đọc bài → gửi Telegram | fetch + send(confirmed=true) | FAIL (model gọi clarify thay vì send) |
| G07_multiturn_correct_topic | Sửa chủ đề AI→blockchain | social_search(query=blockchain) | PASS |
| G08_multiturn_clarify_then_summarize | Thiếu text → cung cấp → tóm tắt | clarify + summarize(max_sentences=2) | PASS |
| G09_multiturn_switch_news_to_tweets | Chuyển web→Twitter | social_search(query=Elon Musk, search_type=Top) | PASS |
| G10_multiturn_parallel_then_format | Tìm web+tweet → format bullets | lookup + social_search + format(bullets) | PASS |

## B4. Live Chat Evidence
## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "5 thông tin chi tiết về OpenAI mới nhất hôm nay" | lookup(query=OpenAI, topic=news, timeframe=day) | v0 | Trả về 5 tin OpenAI |
| 1 | "5 bài báo hôm nay về OpenAI" | lookup(query=OpenAI, topic=news, timeframe=day) | v0 | Trả về 5 bài báo |
| 1-4 | "5 bài báo về OpenAI" → "gửi vào telegram" → "có" → "có" | lookup → clarify → send | v1 | Gửi Telegram thành công |
| 1-2 | "2 bài viết AI + gửi tele" → "có" | clarify → lookup + social_search + format + send | v6 | Gửi Telegram thành công |
| 1-2 | "gửi 3 bài báo bóng đá VN bằng tele" → "có" | clarify → lookup + send | v6 | Gửi Telegram thành công |
| 1 | "Tóm tắt văn bản dài…" | (model không gọi summarize) | v6 | Lỗi: model tóm tắt thủ công |
| 1 | "Tweet mới nhất của Sam Altman?" | timeline(screenname=sama) | v6 | Trả về tweet |

## B5. Bonus Evidence
## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | transcripts/*.transcript.json | Gửi tin nhắn đúng kênh Telegram | clarify(yes_no) xác nhận trước khi gửi |
| arXiv/company policy | (tools sẵn có) | papers + paper_text + policy hoạt động | Rate limit 3s cho arXiv |
| UI (Streamlit) | app.py | Chat interface + tool expanders + transcript logging | Chạy localhost:8501, cần --server.fileWatcherType none |

## B6. Reflection
## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?** Routing rules (tool nào cho câu nào), name→handle mapping, send 3-step flow, out-of-scope detection, parallel tool calls, format sau search, "never fabricate results".
- **Which fixes belonged in `tools.yaml`?** Mô tả tool `send` rõ ràng hơn (bắt buộc confirmed=true, required params), thêm tool `summarize` với parameters.
- **Which failure needed manual review instead of automatic grading?** G06 (send flow) — eval kỳ vọng clarify+send cùng lúc nhưng thực tế clarify sẽ pause conversation. Phải sửa eval case cho thực tế hơn.
- **What would you improve next?** Thêm tool `translate` để dịch kết quả, cải thiện `summarize` dùng LLM thay vì extractive, thêm eval case cho edge cases (text rỗng, URL lỗi, API timeout).