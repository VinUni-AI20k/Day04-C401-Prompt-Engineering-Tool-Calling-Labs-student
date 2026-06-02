# Day 04 Lab v2 Report — Research Agent

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
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?