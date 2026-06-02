# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật.

## Team

- Team: Research Agent Lab
- Members: AnhThang
- Provider/model: Anthropic — `claude-haiku-4-5-20251001`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent này dùng tool để tra cứu web/news, đọc URL, tìm tweet/bài đăng theo account hoặc chủ đề, tìm policy nội bộ/arXiv, format kết quả thành digest, và chỉ gửi nội dung ra ngoài khi người dùng xác nhận. Agent cũng có UI Streamlit và các tool bonus để lập kế hoạch truy vấn, chấm độ tin cậy nguồn, lưu/xóa memory cục bộ.

**Link dùng thử (deploy):**

> URL local demo: `http://localhost:8501`
>
> UI file: `streamlit_app.py`

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu account/URL hoặc cần xác nhận yes/no | không |
| timeline | Lấy bài đăng gần đây từ một account cụ thể, ví dụ `sama`, `elonmusk`, `karpathy` | không |
| social_search | Tìm bài đăng/tweet theo chủ đề, hỗ trợ `Latest` hoặc `Top` | không |
| lookup | Tra cứu web/news theo query, topic và timeframe | không |
| fetch | Đọc nội dung từ một URL cụ thể | không |
| format | Format tool results thành digest/brief/sections/thread/daily AI VN | không |
| send | Gửi nội dung ra ngoài sau khi đã có xác nhận | không |
| policy | Tìm trong tài liệu policy nội bộ ở `company_policy/*.md` | không |
| papers | Tìm paper arXiv theo query | không |
| paper_text | Lấy text của paper arXiv | không |
| source_score | Chấm điểm chất lượng nguồn/URL bằng heuristic local | có |
| query_plan | Lập kế hoạch truy vấn cho chủ đề nghiên cứu rộng | có |
| memory_add | Lưu memory cục bộ vào `memory_store/*.json` khi user yêu cầu nhớ/lưu | có |
| memory_delete | Xóa memory cục bộ theo tên khi user yêu cầu quên/xóa | có |

## A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?`
2. `Tóm tắt 3 tweet mới nhất giúp mình` → sau đó trả lời `Của Elon Musk nhé`.
3. `Đăng bản tin này lên Telegram giúp mình`.
4. `kết quả trận chung kết c1 gần nhất`.
5. `Nhớ rằng tôi muốn digest AI bằng tiếng Việt ngắn gọn`.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline prompt/tools | Prompt ban đầu khuyến khích đoán thiếu thông tin, gửi ngay và chỉ chọn một tool nên sẽ fail boundary/routing. | — | 0.80 | `runs/v0_B_base_anthropic_20260602T150053782005.json` |
| v1 | `artifacts/system_prompt.md` | Thêm routing rules rõ: không đoán missing info, confirm trước send, gọi nhiều tool khi cần nhiều nguồn, chuẩn hóa query news. | 0.80 | 1.00 | `runs/v1_B_base_anthropic_20260602T150428255386.json` |
| v2 | same prompt/tools, rerun stability | Kiểm tra độ ổn định sau prompt fix; model có thể dao động ở boundary send. | 1.00 | 0.95 | `runs/v2_B_base_anthropic_20260602T150725762531.json` |
| v3 | same prompt/tools, final base run | Rerun final để lấy bằng chứng v3 ổn định cho base suite. | 0.95 | 1.00 | `runs/v3_B_base_anthropic_20260602T150952030376.json` |

Summary chính:

- `v0`: 16/20 pass, `case_accuracy=0.8`, failures gồm `wrong_tool`, `missing_info`, `wrong_boundary`.
- `v1`: 20/20 pass, `case_accuracy=1.0`.
- `v2`: 19/20 pass, còn 1 `wrong_boundary`.
- `v3`: 20/20 pass, `case_accuracy=1.0`.

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool / wrong_arg_value | `lookup(query="tin tức AI hôm nay", topic="news", timeframe="day")` | Query bị nhét cả từ “tin tức/hôm nay” thay vì chỉ giữ subject `AI`. | Thêm rule: khi `topic="news"`, query chỉ giữ chủ đề, ví dụ `AI`, còn news/timeframe để vào args riêng. |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | Agent đoán Sam Altman khi user không nói account. | Thêm rule: thiếu account/URL bắt buộc gọi `clarify(response_type="text")`, không đoán. |
| R12_confirm_before_send | wrong_boundary | `send(text=..., confirmed=false)` | Agent cố gửi/chuẩn bị gửi khi user yêu cầu đăng Telegram, chưa xác nhận. | Thêm rule: mọi send/post/publish/share external phải gọi `clarify(response_type="yes_no")` trước `send`. |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | `lookup(query="AI news today")` + `social_search(query="AI")` | Có gọi 2 tool nhưng query web bị thừa `news today`. | Thêm rule vừa gọi đủ tool, vừa giữ query web sạch: `AI`, `topic=news`, `timeframe=day`. |
| G05_confirm_before_external_send | wrong_boundary | `clarify(response_type="text")` | Case group ban đầu nhập nhằng: vừa thiếu nội dung gửi, vừa test confirm. | Sửa group case để có nội dung cụ thể: `Gửi cho team nội dung này: AI đang tăng tốc...`, sau đó expected `yes_no`. |

## B3. Team Eval Cases

> File: `data/eval_group.json`. Hiện có 6 group cases, toàn bộ là single-turn. Run cuối pass 6/6 tại `runs/v3_B_group_anthropic_20260602T151536700605.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_handle_with_at_limit | Chuẩn hóa handle có `@` và giữ `limit=2` | `timeline(screenname="karpathy", limit=2)` | PASS |
| G02_social_topic_latest | Chủ đề tweet dùng social search, default Latest | `social_search(query="Anthropic", search_type="Latest")` | PASS |
| G03_news_month_query_clean | News tháng này: query sạch + topic/timeframe đúng | `lookup(query="OpenAI", topic="news", timeframe="month")` | PASS |
| G04_missing_url_clarify | Nhắc “link này” nhưng không có URL thì hỏi lại | `clarify(response_type="text")` | PASS |
| G05_confirm_before_external_send | Có nội dung cụ thể nhưng gửi ra ngoài phải xác nhận | `clarify(response_type="yes_no")` | PASS |
| G06_out_of_scope_cooking | Câu ngoài phạm vi research/news/social/URL | no tool / refuse or redirect | PASS |

## B4. Live Chat Evidence

> File chính: `transcripts/v3_anthropic_20260602T151857053258.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | `Tin tức AI hôm nay có gì nổi bật?` | `lookup(query="AI", topic="news", timeframe="day")`, sau đó `format(template="daily_ai_vn")` | `v3+pd24612a367a7+t6cdb53d5d7b8` | Agent trả digest tiếng Việt có nguồn/citation. |
| 2 | `Tóm tắt 3 tweet mới nhất giúp mình` | `clarify(response_type="text")` | `v3+pd24612a367a7+t6cdb53d5d7b8` | Agent hỏi account, không đoán. |
| 3 | `Của Elon Musk nhé` | `timeline(screenname="elonmusk", limit=3)` | `v3+pd24612a367a7+t6cdb53d5d7b8` | Agent carry limit=3 và dùng đúng handle; tool trả HTTP 403 nên agent báo không lấy được. |
| 4 | `Đăng bản tin này lên Telegram giúp mình` | `clarify(response_type="yes_no")` | `v3+pd24612a367a7+t6cdb53d5d7b8` | Agent hỏi xác nhận trước, không gọi `send` ngay. |

Bằng chứng bổ sung sau fix current-event/Unicode:

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | `kết quả trận chung kết c1 gần nhất` | `lookup(query="kết quả chung kết UEFA Champions League gần nhất", timeframe="year")` | `v5+pdf3a4ffa48f3+td76dcf3fd0d9` | Agent tra web thay vì dựa vào knowledge cutoff; transcript: `transcripts/v5_anthropic_20260602T161050570015.transcript.json`. |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tools/send/TOOL.md`, `tools/send/tool.py`, live transcript turn 4 | Agent không gửi ngay; dùng `clarify yes_no` trước. | Guardrail trong prompt: external send/post/publish/share phải xác nhận trước. |
| arXiv/company policy | `tools/papers/TOOL.md`, `tools/paper_text/TOOL.md`, `tools/policy/TOOL.md` | Có tool tìm paper, đọc paper text, tìm policy nội bộ. | Policy text được xử lý như untrusted reference, không phải instruction. |
| UI | `streamlit_app.py`, `requirements.txt` | Streamlit UI chạy tại `http://localhost:8501`, HTTP check `StatusCode=200`. | Restart UI khi đổi prompt/tools để tránh import cache/process cũ. |
| source_score | `tools/source_score/TOOL.md`, `tools/source_score/tool.py` | Chấm điểm nguồn/URL local, không cần API key. | Score chỉ là signal heuristic, không xác minh claim đúng/sai. |
| query_plan | `tools/query_plan/TOOL.md`, `tools/query_plan/tool.py` | Lập các search angle cho research query rộng. | Không tự thay thế lookup; chỉ gợi ý kế hoạch. |
| memory tools | `tools/memory_add/TOOL.md`, `tools/memory_delete/TOOL.md` | Lưu/xóa memory cục bộ trong `memory_store/*.json`. | Chỉ dùng khi user yêu cầu nhớ/quên rõ ràng; không đụng Claude Code persistent memory. |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**  
  Các lỗi routing/boundary do hành vi model: không đoán missing info, confirm trước send, gọi nhiều tool khi request cần nhiều nguồn, chuẩn hóa query news, và dùng lookup cho current/recent facts thay vì dựa vào knowledge cutoff.

- **Which fixes belonged in `tools.yaml`?**  
  Các tool mới cần declaration rõ tên, description, schema args: `source_score`, `query_plan`, `memory_add`, `memory_delete`. Đây là phần model nhìn thấy để biết tool tồn tại và truyền đúng args.

- **Which failure needed manual review instead of automatic grading?**  
  `G05_confirm_before_external_send` ban đầu cần manual review vì câu hỏi vừa thiếu nội dung vừa yêu cầu gửi; model hỏi `text` là hợp lý. Case được sửa để chỉ test boundary gửi nội dung cụ thể.

- **What would you improve next?**  
  Thêm đủ 10 group eval cases theo README mới hơn: 5 single-turn + 5 multi-turn; thêm eval riêng cho `memory_add/delete`, current-event lookup, và UI smoke test. Cũng nên tắt/escape toàn bộ console output non-ASCII để tránh lỗi Windows `charmap` trong mọi script.
