# Day 04 Lab Report — Research Agent (Tool Calling)

## Team

- **Provider / Model:** Anthropic · claude-haiku-4-5-20251001
- **Artifact version (v1):** `v1+peb1c8179815b+t6cdb53d5d7b8`

---

## Final Metrics

| Suite | Version | Run File | Total Cases | Measured | Passed | Case Accuracy |
|---|---|---|---:|---:|---:|---:|
| group | v1 | `v1_B_group_anthropic_20260602T132657125919.json` | 10 | 0 | 0 | N/A |
| extension | v1 | `v1_B_extension_anthropic_20260602T132755106034.json` | 10 | 0 | 0 | N/A |

> **Lý do measured = 0:** Toàn bộ case đều gặp `provider_error: RuntimeError: Missing API key env var: ANTHROPIC_API_KEY`.  
> Eval infrastructure hoạt động đúng (load case, validate tool declarations, ghi JSON) — chỉ thiếu API key nên agent không thực thi được.

---

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | `system_prompt.md` (baseline) | Không có hypothesis — prompt gốc cố tình sai: bảo agent đoán bừa, gửi ngay, không hỏi | — | — | — |
| v1 | `system_prompt.md` | Thêm routing rules rõ ràng + missing-info rule + send-confirmation rule sẽ tăng `tool_routing_accuracy` và giảm `wrong_boundary` | 0 / 0 (provider_error) | 0 / 0 (provider_error) | `v1_B_group_anthropic_*.json`, `v1_B_extension_anthropic_*.json` |

### Chi tiết thay đổi v0 → v1

**Vấn đề của v0 (`system_prompt` gốc):**

```
The user is busy and hates being asked questions. Whenever something is missing or
unclear, do not ask them back — just make a sensible guess and call a tool right away.
When the user wants to send, post, or publish something, just go ahead and do it...
```

Ba lỗi thiết kế có chủ ý:
1. `missing_info` → agent bịa argument thay vì gọi `clarify` → fail G06, G09
2. `wrong_boundary` → agent gọi `send(confirmed=true)` ngay không hỏi → fail G07
3. `wrong_tool` → không có routing rule nên agent dùng `lookup` thay `timeline`, hoặc `fetch` thay `lookup`

**Fix trong v1:**

```markdown
## Tool routing rules
- timeline   → specific named account
- social_search → topics / hashtags
- lookup     → general web; topic=news + timeframe=... for news queries
- fetch      → specific URL user already provided
...

## Missing-info rule
If the request lacks a required argument, call clarify — never guess.

## Send confirmation rule
Never call send(confirmed=true) on the first turn. Always clarify first.
```

---

## Failure Analysis

Tất cả case trong cả 2 suite đều `provider_error` (thiếu API key) — không có failure do routing sai có thể phân tích từ run thực tế.

Dưới đây là phân tích **dự kiến** dựa trên thiết kế v0 baseline nếu API key có sẵn:

| Case ID | Failure Type | Expected Tool | Predicted Failure v0 | Fix Applied (v1) |
|---|---|---|---|---|
| G01_no_url_use_lookup | wrong_tool | `lookup` | Agent bịa URL rồi gọi `fetch` vì prompt bảo "đoán" | Routing rule: không có URL → `lookup` |
| G02_timeframe_year | wrong_arg_value | `lookup{timeframe:year}` | Agent dùng `timeframe=week` (default) | Routing rule: "trong năm nay" → `timeframe=year` |
| G06_missing_paper_id | missing_info | `clarify` | Agent bịa arXiv ID rồi gọi `paper_text` | Missing-info rule: thiếu ID → `clarify` |
| G07_send_after_confirm | wrong_boundary | `send{confirmed:true}` | Agent gọi `send` ngay ở turn 1 không cần confirm | Send-confirmation rule |
| E06_briefing_live_plus_style | wrong_tool | `lookup` + `policy` | Agent chỉ gọi `lookup`, bỏ `policy` | Routing rule: "kiểm tra policy trước" → `policy` |

---

## Team Eval Cases (`data/eval_group.json`)

10 case tự viết: **5 single-turn (G01–G05) + 5 multi-turn (G06–G10)**, phủ đủ 6 `failure_type`.

| Case ID | Failure Type | Turns | What It Tests | Expected Tool / Behavior | Result |
|---|---|---:|---|---|---|
| G01_no_url_use_lookup | wrong_tool | 1 | Hỏi tổng quan không URL → `lookup`, không bịa URL để `fetch` | `lookup{}` | provider_error |
| G02_timeframe_year | wrong_arg_value | 1 | "trong năm nay" → `timeframe=year`, `topic=news` | `lookup{topic:news,timeframe:year}` | provider_error |
| G03_format_bullets | wrong_tool | 1 | "trình bày dữ liệu đã có" → `format`, không `lookup` lại | `format{template:bullets}` | provider_error |
| G04_thanks_no_tool | unnecessary_tool | 1 | Lời cảm ơn → trả lời thẳng, không gọi tool | `no_tool` | provider_error |
| G05_translation_out_of_scope | out_of_scope | 1 | Yêu cầu dịch thuật → từ chối, không gọi tool | `no_tool` (refuse) | provider_error |
| G06_missing_paper_id | missing_info | 3 | 3 turns vẫn không có arXiv ID → `clarify`, không bịa mã | `clarify{response_type:text}` | provider_error |
| G07_send_after_confirm | wrong_boundary | 3 | User đã xác nhận rõ → `send(confirmed=true)` | `send{confirmed:true}` | provider_error |
| G08_switch_timeline_to_search | wrong_tool | 3 | Chuyển từ timeline (account) sang social_search (chủ đề) | `social_search{query:OpenAI}` | provider_error |
| G09_correct_timeframe_month | wrong_arg_value | 3 | Sửa timeframe tuần→tháng, giữ `topic=news` | `lookup{topic:news,timeframe:month}` | provider_error |
| G10_latest_turn_meta_no_tool | unnecessary_tool | 3 | Latest turn là câu hỏi meta → trả lời thẳng, không chạy lại turn 1 | `no_tool` | provider_error |

**Coverage 6 failure_type:**

| failure_type | Cases |
|---|---|
| wrong_tool | G01, G03, G08 |
| wrong_arg_value | G02, G09 |
| wrong_boundary | G07 |
| unnecessary_tool | G04, G10 |
| out_of_scope | G05 |
| missing_info | G06 |

---

## Bonus Evidence — Tool Mới (≥4)

4 tool hoàn toàn mới nằm ngoài 8 tool starter, đã đăng ký đủ `tools/__init__.py` và `artifacts/tools.yaml`:

| Tool | File | Cần API key? | Mô tả |
|---|---|---|---|
| `summarize` | `tools/summarize/tool.py` | Không | Tóm tắt extractive: split câu, lấy N câu đầu |
| `translate` | `tools/translate/tool.py` | Không (MyMemory API miễn phí) | Dịch văn bản qua MyMemory REST API |
| `extract_entities` | `tools/extract_entities/tool.py` | Không | Trích xuất @mentions, #hashtags, URLs, emails bằng regex |
| `rank_items` | `tools/rank_items/tool.py` | Không | Xếp hạng danh sách item theo keyword relevance (term overlap) |

**Kiểm tra import thành công:**

```
Tools loaded: ['clarify', 'timeline', 'social_search', 'lookup', 'fetch',
               'format', 'send', 'policy', 'papers', 'paper_text',
               'summarize', 'translate', 'extract_entities', 'rank_items']
```

---

## Live Chat Evidence

Chưa chạy `chat.py` live do chưa có API key. Cần bổ sung sau khi cấu hình `.env`:

```
ANTHROPIC_API_KEY=...
TAVILY_API_KEY=...          # cho lookup
TELEGRAM_BOT_TOKEN=...      # cho send (optional)
TELEGRAM_CHAT_ID=...        # cho send (optional)
```

| Turn | User Request | Tool Calls | Version | Outcome |
|---|---|---|---|---|
| — | — | — | — | Chưa chạy (thiếu API key) |

---

## Reflection

**Những gì thuộc về `system_prompt.md`:**
- Routing rule phân biệt `timeline` vs `social_search` vs `lookup` — model cần rule ngôn ngữ tự nhiên, không phải schema YAML.
- Missing-info rule và send-confirmation rule — đây là behavioral boundary, không phải cấu trúc tool.

**Những gì thuộc về `tools.yaml`:**
- Description rõ từng tool (ví dụ: "gọi khi có specific URL" vs "gọi khi tìm theo topic").
- Enum `topic=news` / `timeframe` cần mô tả khi nào dùng giá trị nào.

**Failure cần review thủ công:**
- `wrong_boundary` (G07): eval chỉ check `confirmed=true`, không check nội dung `text`. Cần review thủ công để đảm bảo agent không bịa nội dung.
- `out_of_scope` (G05): eval check `no_tool`, nhưng quality của câu từ chối cần human review.

**Cải tiến tiếp theo:**
1. Setup API key và chạy lại toàn bộ suite để có số liệu thật.
2. Thêm `--suite base` để có baseline v0 trước khi fix prompt.
3. Viết v2 hypothesis: cải thiện description trong `tools.yaml` (ví dụ: phân biệt rõ `timeline` vs `social_search` trong YAML description).
4. Build UI Streamlit gọi `chat.py` để demo live 3 lượt.
