# Đề xuất phân công — Day 04 C401: Prompt Engineering & Tool Calling Lab

**Mục tiêu:** đạt điểm cao nhất, bao gồm trúng **bonus point** (UI + >3 tool mới).
**Quy mô:** 3 người · **Thời lượng:** 4h.
**Repo:** `Day04-C401-Prompt-Engineering-Tool-Calling-Labs-student`

---

## Nguyên tắc chia việc (đọc trước)

1. **Vòng tối ưu `v1 → v2 → v3` là tuần tự, KHÔNG song song được.**
   `version_log.csv` yêu cầu *mỗi version đổi đúng một giả thuyết* (one hypothesis per version), và mỗi version build trên version trước. Nếu nhiều người cùng sửa `system_prompt.md`/`tools.yaml` một lúc thì log loạn, mất điểm phần **methodology** — vốn được chấm nặng nhất ("report dựa trên log thật").
   → Chia theo **trục công việc**, không chia kiểu "ai cũng sửa prompt".

2. **Một người duy nhất ghi `artifacts/` (P1).** Người khác đưa nội dung dạng block để paste, tránh merge conflict trong 4h.

3. **Điểm cao nhất bắt buộc trúng combo bonus:** dựng **UI** *VÀ* viết thêm **>3 tool mới** (tức **≥4 tool hoàn toàn mới**, ngoài 8 tool có sẵn). Đây là phần thưởng giá trị cao nhất → phải có người chịu trách nhiệm rõ ràng (P2).

---

## Người 1 — Agent Lead - Đạt/ Optimization Driver

Giữ **xương sống** của bài; là **single-writer** của `artifacts/`.

- Setup `.env`, key provider, chạy `scripts/preflight_provider.py`, rồi chạy **baseline `v0`** (`--suite base`).
- Đọc run JSON từng case FAIL: `observed_mismatch` + `failures` + `actual_tool_calls`; đặt giả thuyết *vì sao* route sai (thiếu rule routing? thiếu convention args? prompt khuyến khích đoán/gửi sớm?).
- Chạy **`v1`, `v2`, `v3`**, mỗi version đổi **đúng một thứ** (một dòng prompt hoặc một tool description) để kiểm chứng giả thuyết; so `metric_before` / `metric_after`. Nếu không cải thiện → đổi giả thuyết.
- **Người duy nhất ghi `tools.yaml`**: P2 đưa block YAML để paste, P1 commit.
- Điền đầy đủ `version_log.csv` (đủ `v0, v1, v2, v3` kèm `prompt_hash` / `tools_hash` / `run_file`).

> Phần "sửa để gọi đúng tool": cải thiện **declaration** của 8 tool có sẵn chính là đòn bẩy cho `tool_routing_accuracy` và `argument_accuracy`. P2 đề xuất mô tả tốt hơn, P1 áp dụng **như một hypothesis trong version log** để chứng minh tác động — vừa sửa được routing vừa ghi điểm methodology.

**Metric theo dõi:** `case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy`.

---

## Người 2 - Mạnh — Tools & UI Engineer

Lane build **song song**; mục tiêu duy nhất: **ăn trọn bonus point**.

- Audit code 8 tool có sẵn, fix bug rõ ràng, **draft lại description + param docs** → chuyển cho P1.
- Viết **≥4 tool mới**. Mỗi tool cần đủ bộ:
  - `tools/<tool_name>/tool.py` (self-contained)
  - `tools/<tool_name>/TOOL.md` (frontmatter + notes)
  - đăng ký ở `tools/__init__.py` (`TOOL_FUNCTIONS`) **và** `artifacts/tools.yaml`
- Lưu ý các tool bonus gợi ý (`send`, `policy`, `papers`, `paper_text`): **nếu đã có sẵn trong repo thì KHÔNG tính là "mới"**. Cần tool thật sự mới, ví dụ: `summarize`, `dedupe`, `rank_items`, `extract_entities`, `translate`, `cache_lookup`…
- `send` (action tool): **chỉ gửi khi `confirmed=true`**, phải hỏi xác nhận trước.
- Dựng **UI Streamlit** (nhanh hơn Vercel nhiều cho deadline 4h) gọi lại agent loop / `chat.py`.
- **Bàn giao tool mới cho P1 trước ~2:15** để lần chạy `v3` final gồm đủ chúng.

---

## Người 3 - Thái — Eval & Report Lead

Sở hữu phần **đo lường** và **report** — nơi ra nhiều điểm nhất.

- Viết **10 case** vào `data/eval_group.json`: **5 single-turn + 5 multi-turn**, `phase: "B"`, phủ đủ 6 `failure_type`. Seed gợi ý:

  | `failure_type` | Ý tưởng case |
  |---|---|
  | `wrong_tool` | "X dạo này tweet gì" → phải `timeline`, không `lookup`/`social_search` |
  | `wrong_arg_value` | ép sai `search_type` Latest/Top hoặc `timeframe`/`topic` |
  | `wrong_boundary` | "đăng tin lên Telegram" → phải hỏi confirm trước, không gửi ngay |
  | `unnecessary_tool` | câu trả lời được không cần tool → `no_tool` |
  | `out_of_scope` | request ngoài domain research |
  | `missing_info` | request thiếu account/URL → phải `clarify` trước |

- Chạy `--suite group` + `--suite extension`; parse log bằng `scripts/parse_runs.py` ra `analysis/*.csv`.
- Chạy `chat.py` live **≥3 lượt** (1 normal · 1 thiếu-info-rồi-bổ-sung · 1 Telegram-confirm) → lưu `transcripts/*.transcript.json`.
- Viết `artifacts/REPORT.md` **bám số liệu thật**: bảng metric trước/sau từng version + narrative *giả thuyết → kết quả* + phân tích failure.
- Đóng gói submission cuối + sanity check.

---

## Lịch 4h theo từng người

| Mốc | Người 1 (Agent Lead) | Người 2 (Tools & UI) | Người 3 (Eval & Report) |
|---|---|---|---|
| 0:00–0:25 | Setup `.env`, provider key, preflight | Setup key tool (Tavily/Firecrawl/RapidAPI/Telegram) | Đọc format trong `samples/`, hỗ trợ setup |
| 0:25–0:55 | Chạy **baseline v0**, đọc run JSON | Audit 8 tool, fix bug | Nghiên cứu schema `eval_base.json`, `observed_mismatch` |
| 0:55–1:45 | **v1, v2** (analyze → hypothesis → rerun) | Draft declaration mới → gửi P1; bắt đầu viết tool mới | Viết 10 eval case (5 single + 5 multi) |
| 1:45–2:15 | Tinh chỉnh, nhận declaration từ P2 | Hoàn thiện ≥4 tool mới + đăng ký | Chạy group + extension eval, parse ra CSV |
| 2:15–2:45 | Tích hợp tool mới, chạy **v3** final | **Bàn giao tool cho P1**, bắt đầu UI Streamlit | Chạy `chat.py` live ≥3 lượt → transcripts |
| 2:45–3:50 | Hoàn thiện `version_log.csv`, hỗ trợ số liệu | Dựng + test UI Streamlit | Viết `REPORT.md` từ log thật |
| 3:50–4:00 | Sanity check `artifacts/` | Hỗ trợ đóng gói | Đóng gói submission + final check |

---

## Điểm đồng bộ giữa 3 người

- Sau khi P1 xong **v0**, P3 viết eval case ngay (case không phụ thuộc version prompt) → chạy song song.
- P2 build tool song song từ đầu; **hạn chót bàn giao cho P1 lúc ~2:15**.
- P3 chốt report **sau cùng** vì cần `version_log` + `runs/` đầy đủ từ P1.

---

## ⚠️ Bẫy mất điểm — cảnh báo cả nhóm

- **Đổi tên tool phải đồng bộ ở CẢ những nơi sau**, nếu không eval báo `not declared in tools.yaml` và chấm sai sạch:
  1. `artifacts/tools.yaml` (field `name`)
  2. `tools/__init__.py` (key trong `TOOL_FUNCTIONS`)
  3. `data/eval_base.json` **và** `data/eval_research_extension.json` (`expect.tool_calls[].name`)
- **KHÔNG sửa nội dung case** trong `eval_base.json`.
- Tool mới phải đăng ký ở **cả** `__init__.py` **và** `tools.yaml`.
- **KHÔNG commit `.env`** hoặc API key.

---

## Checklist nộp bài (`starter_v0/`)

- [ ] `artifacts/system_prompt.md`
- [ ] `artifacts/tools.yaml`
- [ ] `artifacts/version_log.csv` (đủ `v0, v1, v2, v3`)
- [ ] `artifacts/REPORT.md`
- [ ] `data/eval_group.json` (≥10 case: 5 single + 5 multi)
- [ ] `runs/*.json`
- [ ] `analysis/*.csv`
- [ ] `transcripts/*.transcript.json`
- [ ] Code tool mới (≥4) + UI Streamlit
- [ ] ❌ KHÔNG có `.env` / API key
