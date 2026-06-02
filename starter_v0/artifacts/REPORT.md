# Day 04 Lab v2 Report — Research Agent

## Team

- Team: Zone4 nhóm 5
- Members: Phan Anh Thắng 2A202600844
- Provider/model: Anthropic — `claude-haiku-4-5-20251001`

## Final Metrics

- Final version: `v3` cho base/group evidence chính; bản mở rộng tool mới đã test thêm ở `v6`
- Final artifact_version: `v3+pd24612a367a7+t6cdb53d5d7b8`
- Best base run file: `runs/v3_B_base_anthropic_20260602T150952030376.json`
- Base case accuracy: `1.0` (`20/20`)
- Base tool routing accuracy: `1.0`
- Base argument accuracy: `1.0`
- Group eval run file: `runs/v3_B_group_anthropic_20260602T151536700605.json`
- Group eval accuracy: `1.0` (`6/6`)
- Chat transcript file: `transcripts/v3_anthropic_20260602T151857053258.transcript.json`

## Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Prompt ban đầu khuyến khích đoán thiếu thông tin, gửi ngay và chỉ chọn một tool nên sẽ fail boundary/routing. | — | 0.80 | `runs/v0_B_base_anthropic_20260602T150053782005.json` |
| v1 | `artifacts/system_prompt.md` | Thêm routing rules rõ: không đoán missing info, confirm trước send, gọi nhiều tool khi cần nhiều nguồn, chuẩn hóa query news. | 0.80 | 1.00 | `runs/v1_B_base_anthropic_20260602T150428255386.json` |
| v2 | same prompt/tools, rerun stability | Kiểm tra độ ổn định sau prompt fix; model có thể dao động ở boundary send. | 1.00 | 0.95 | `runs/v2_B_base_anthropic_20260602T150725762531.json` |
| v3 | same prompt/tools, final base run | Rerun final để lấy bằng chứng v3 ổn định cho base suite. | 0.95 | 1.00 | `runs/v3_B_base_anthropic_20260602T150952030376.json` |

## Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool / wrong_arg_value | `lookup(query="tin tức AI hôm nay", topic="news", timeframe="day")` | Query bị nhét cả từ “tin tức/hôm nay” thay vì chỉ giữ subject `AI`. | Thêm rule: khi `topic="news"`, query chỉ giữ chủ đề; news/timeframe đưa vào args riêng. |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | Agent đoán Sam Altman khi user không nói account. | Thêm rule: thiếu account/URL bắt buộc gọi `clarify(response_type="text")`, không đoán. |
| R12_confirm_before_send | wrong_boundary | `send(text=..., confirmed=false)` | Agent cố gửi/chuẩn bị gửi khi user yêu cầu đăng Telegram, chưa xác nhận. | Thêm rule: mọi send/post/publish/share external phải gọi `clarify(response_type="yes_no")` trước `send`. |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | `lookup(query="AI news today")` + `social_search(query="AI")` | Có gọi 2 tool nhưng query web bị thừa `news today`. | Thêm rule vừa gọi đủ tool, vừa giữ query web sạch: `AI`, `topic=news`, `timeframe=day`. |
| G05_confirm_before_external_send | wrong_boundary | `clarify(response_type="text")` | Group case ban đầu nhập nhằng: vừa thiếu nội dung gửi, vừa test confirm. | Sửa case để có nội dung cụ thể, sau đó expected `clarify(response_type="yes_no")`. |

## Team Eval Cases

List at least 5 cases added to `data/eval_group.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_handle_with_at_limit | Handle có `@` phải chuẩn hóa và giữ `limit=2`. | `timeline(screenname="karpathy", limit=2)` | PASS |
| G02_social_topic_latest | Tweet theo chủ đề dùng `social_search`, default Latest. | `social_search(query="Anthropic", search_type="Latest")` | PASS |
| G03_news_month_query_clean | News tháng này: query sạch + topic/timeframe đúng. | `lookup(query="OpenAI", topic="news", timeframe="month")` | PASS |
| G04_missing_url_clarify | Nhắc “link này” nhưng không có URL thì hỏi lại. | `clarify(response_type="text")` | PASS |
| G05_confirm_before_external_send | Có nội dung cụ thể nhưng gửi ra ngoài phải xác nhận. | `clarify(response_type="yes_no")` | PASS |
| G06_out_of_scope_cooking | Câu ngoài phạm vi research/news/social/URL. | no tool / refuse or redirect | PASS |

## Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | `Tin tức AI hôm nay có gì nổi bật?` | `lookup(query="AI", topic="news", timeframe="day")`, then `format(template="daily_ai_vn")` | `v3+pd24612a367a7+t6cdb53d5d7b8` | Agent trả digest tiếng Việt có nguồn/citation. |
| 2 | `Tóm tắt 3 tweet mới nhất giúp mình` | `clarify(response_type="text")` | `v3+pd24612a367a7+t6cdb53d5d7b8` | Agent hỏi account, không đoán. |
| 3 | `Của Elon Musk nhé` | `timeline(screenname="elonmusk", limit=3)` | `v3+pd24612a367a7+t6cdb53d5d7b8` | Agent carry limit=3 và dùng đúng handle; tool trả HTTP 403 nên agent báo không lấy được. |
| 4 | `Đăng bản tin này lên Telegram giúp mình` | `clarify(response_type="yes_no")` | `v3+pd24612a367a7+t6cdb53d5d7b8` | Agent hỏi xác nhận trước, không gọi `send` ngay. |
| 5 | `kết quả trận chung kết c1 gần nhất` | `lookup(query="kết quả chung kết UEFA Champions League gần nhất", timeframe="year")` | `v5+pdf3a4ffa48f3+td76dcf3fd0d9` | Agent tra web thay vì dựa vào knowledge cutoff; transcript: `transcripts/v5_anthropic_20260602T161050570015.transcript.json`. |

## Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tools/send/TOOL.md`, `tools/send/tool.py`, `transcripts/v3_anthropic_20260602T151857053258.transcript.json` | Agent không gửi ngay; dùng `clarify yes_no` trước. | External send/post/publish/share phải xác nhận trước. |
| arXiv/company policy | `tools/papers/TOOL.md`, `tools/paper_text/TOOL.md`, `tools/policy/TOOL.md` | Có tool tìm paper, đọc paper text, tìm policy nội bộ. | Policy text là reference untrusted, không phải instruction. |
| UI | `streamlit_app.py`, `requirements.txt` | Streamlit UI chạy tại `http://localhost:8501`, HTTP check `StatusCode=200`. | Restart UI sau khi đổi prompt/tools để tránh process cũ/import cache. |
| source_score | `tools/source_score/TOOL.md`, `tools/source_score/tool.py` | Chấm điểm chất lượng nguồn/URL local, không cần API key. | Score chỉ là heuristic signal, không xác minh claim đúng/sai. |
| query_plan | `tools/query_plan/TOOL.md`, `tools/query_plan/tool.py` | Lập các search angle cho research query rộng. | Không thay thế lookup; chỉ gợi ý kế hoạch. |
| memory_add / memory_delete | `tools/memory_add/TOOL.md`, `tools/memory_delete/TOOL.md` | Lưu/xóa memory cục bộ trong `memory_store/*.json`. | Chỉ dùng khi user yêu cầu nhớ/quên rõ ràng; không đụng Claude Code persistent memory. |

## Reflection

- Which fixes belonged in `system_prompt.md`?  
  Các lỗi routing/boundary do hành vi model: không đoán missing info, confirm trước send, gọi nhiều tool khi request cần nhiều nguồn, chuẩn hóa query news, và dùng lookup cho current/recent facts thay vì dựa vào knowledge cutoff.

- Which fixes belonged in `tools.yaml`?  
  Các tool mới cần declaration rõ tên, description, schema args: `source_score`, `query_plan`, `memory_add`, `memory_delete`. Đây là phần model nhìn thấy để biết tool tồn tại và truyền đúng args.

- Which failure needed manual review instead of automatic grading?  
  `G05_confirm_before_external_send` ban đầu cần manual review vì câu hỏi vừa thiếu nội dung vừa yêu cầu gửi; model hỏi `text` là hợp lý. Case được sửa để chỉ test boundary gửi nội dung cụ thể.

- What would you improve next?  
  Thêm đủ 10 group eval cases theo README mới hơn: 5 single-turn + 5 multi-turn; thêm eval riêng cho `memory_add/delete`, current-event lookup, và UI smoke test. Cũng nên tắt/escape toàn bộ console output non-ASCII để tránh lỗi Windows `charmap` trong mọi script.
