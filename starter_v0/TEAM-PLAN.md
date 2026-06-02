# Kế hoạch dự án (3 người / 3 giờ) — Day04 C401 Research Agent Tool Eval

> Tài liệu kim chỉ nam cho nhóm. Mục tiêu nhóm: **tham vọng điểm thưởng** = làm CẢ HAI: dựng UI (Streamlit) **VÀ** tự viết **>3 tool mới**.

## 0. Bối cảnh (đọc trước khi bắt đầu)

Lab này **không** phải làm "chatbot trả lời hay" mà là **vòng lặp tối ưu dựa trên bằng chứng (evidence-driven)**:
chạy agent thật → đọc run JSON → sửa `system_prompt.md` / `tools.yaml` → chạy lại → ghi version log → viết report.

Điểm mấu chốt đã kiểm chứng trong code:

- **`artifacts/system_prompt.md` hiện tại là prompt "cố tình xấu"**: bảo agent *luôn đoán bừa, không bao giờ hỏi lại, gửi/đăng ngay không xác nhận, luôn làm trong 1 bước*. Đây là thứ phải **viết lại** — nó sẽ fail các case clarify (R10, R11), confirm-before-send (R12), out-of-scope (R08, R14), parallel (R13).
- **`artifacts/tools.yaml` mô tả rất mơ hồ** (mỗi tool 1 dòng chung chung). Không có quy tắc routing, không map tên→handle, không quy ước args (news/timeframe/Top), không nêu ranh giới confirm khi send. Đây là file thứ hai phải làm tốt.
- **Grader (`run_eval.py`)** chấm theo *subset*: đúng tên tool + đúng các args mà case yêu cầu (không cần đủ mọi args). **Phạt tool gọi thừa** (`extra_tool_call`) → rủi ro lớn khi thêm tool mới. Case `no_tool` chạy `tool_choice=None` (được phép không gọi); case khác `tool_choice="required"` (bắt buộc gọi ≥1 tool).
- 10 tool đã khai báo sẵn (6 core + 4 bonus) và đã đăng ký trong `tools/__init__.py`. Yêu cầu "≥5 tool" đã đủ; **bắt buộc thêm ≥1 tool mới** (làm >3 để lấy điểm thưởng).

---

## 1. Mô tả dự án ngắn gọn (2 phút)

Agent nhận request → chọn tool → điền args → chạy tool thật → log JSON → dùng log tối ưu prompt/tool qua version v0→v3.
Đo bằng eval cố định (`data/eval_base.json`, **KHÔNG sửa case**) + eval nhóm tự viết (`data/eval_group.json`).

Metric quan tâm trong run JSON: `summary.case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy`;
per-case `results[*].result.failures` + `observed_mismatch`.

---

## 2. Phân vai 3 người

| Vai | Sở hữu file | Nhiệm vụ chính |
|---|---|---|
| **A — Prompt & Routing Lead** | `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv` | Chạy baseline v0; đọc failure; viết lại prompt + tool descriptions; chạy v1→v3; ghi version log; phần Failure Analysis của report. **Đường găng (critical path).** |
| **B — Tools & Eval Engineer** | `tools/<new_tool>/`, `tools/__init__.py`, `data/eval_group.json` | Viết >3 tool mới (mỗi tool: `tool.py` + `TOOL.md` + đăng ký registry + khai báo `tools.yaml`); smoke-test; viết 10 group eval case (5 single + 5 multi); chạy group eval. |
| **C — UI & Integration/Report Lead** | `ui/` (Streamlit), `transcripts/`, `artifacts/REPORT.md`, git/`.env` | Dựng Streamlit UI gọi agent; chạy `chat.py` lấy ≥3 transcript live; viết REPORT.md; quản lý git + đảm bảo KHÔNG commit `.env`; đóng gói submit. |

**Tránh đụng file:** A sở hữu prompt + tools.yaml. B chỉ *thêm khối tool mới* vào cuối `tools.yaml` rồi báo A merge, không sửa khối A đang chỉnh. Commit nhỏ, gộp thường xuyên (hoặc nhánh git riêng).

---

## 3. Timeline 3 giờ (180 phút) — chạy song song

| Thời gian | A (Prompt/Routing) | B (Tools/Eval) | C (UI/Report) |
|---|---|---|---|
| **0:00–0:20** Kickoff + setup | venv, `.env` keys, `preflight_provider.py --provider openrouter` | cùng setup; đọc `tools/README.md` (contract) | cùng setup; skeleton Streamlit; tạo nhánh git |
| **0:20–0:35** | Chạy **baseline v0** (`--version v0 --suite base`); mở run JSON | Scaffold tool mới #1 (vd `now`) | Streamlit "hello" gọi thử 1 tool |
| **0:35–1:15** Vòng lặp lõi | Đọc failure v0 → viết lại system_prompt + tools.yaml → chạy **v1**, **v2** (mỗi lần đổi 1 giả thuyết, ghi version_log) | Hoàn tất 4 tool mới + TOOL.md + đăng ký + smoke-test | Kết nối Streamlit ↔ agent loop (chọn provider, hiển thị tool calls) |
| **1:15–1:45** | Chạy **v3** (accuracy cao) | Viết 10 group eval case; chạy group eval | Polish UI: show args + kết quả tool |
| **1:45–2:15** Tích hợp | Merge khối tool mới của B vào tools.yaml + prompt, **chạy lại base eval** xác nhận KHÔNG bị `extra_tool_call` | Hỗ trợ A; chốt group eval pass | Chạy `chat.py --version v3` lấy **≥3 transcript** (1 normal, 1 thiếu info rồi bổ sung, 1 yêu cầu "đăng Telegram") |
| **2:15–2:45** Report | Failure Analysis + Reflection | Bảng Team Eval + Bonus (tool mới) | Final Metrics + Version Evidence + Bonus (UI) từ run JSON |
| **2:45–3:00** Đóng gói | Đối chiếu version_log đủ v0–v3 | Đối chiếu tên tool đồng bộ 3 nơi | Chạy **Checklist nộp bài**, xác nhận không có `.env` |

> Lịch rất gấp do nhắm điểm thưởng. Nếu đến **1:45** mà phần bắt buộc (v0–v3 + group eval) chưa chắc → **ưu tiên hoàn thành phần bắt buộc trước**, cắt số tool mới về đúng yêu cầu và làm UI tối giản.

---

## 4. Gợi ý kỹ thuật cụ thể

### 4.1 Viết lại `system_prompt.md` (A) — mã hóa đúng hành vi eval mong đợi

Xóa toàn bộ prompt cũ. Prompt mới cần nêu rõ:

- **Vai trò & phạm vi:** trợ lý research/tin tức/mạng xã hội/web/paper. Ngoài phạm vi (toán, code…) → **từ chối, KHÔNG gọi tool** (R08, R14).
- **Câu hỏi meta** ("bạn là gì, làm được gì") → trả lời thẳng, **không gọi tool** (R09).
- **Quy tắc routing:**
  - Tin/tweet *của một người cụ thể* → `timeline`, map tên→handle: Sam Altman→`sama`, Elon Musk→`elonmusk`, Andrej Karpathy→`karpathy` (R01, R05, M01, M03, M05).
  - Tweet *theo chủ đề* → `social_search`; "phổ biến/top" → `search_type=Top`, mặc định `Latest` (R02, R07).
  - Tin thời sự web → `lookup` `topic=news`; "hôm nay"→`timeframe=day`, "tuần này"→`week` (R03, R06).
  - Đã có **URL cụ thể** → `fetch` đúng url (R04, M04).
  - Request cần **nhiều nguồn** ("web … và tweet …") → gọi **song song** cả `lookup` và `social_search` (R13).
- **Hỏi lại khi thiếu:** thiếu handle / thiếu URL → `clarify` (`response_type=text`), **tuyệt đối không đoán bừa** (R10, R11). (Ngược hẳn prompt cũ.)
- **Ranh giới hành động (write):** "đăng/gửi/publish" → `clarify` (`response_type=yes_no`) xác nhận trước, **không tự gửi** (R12).
- **Multi-turn:** chỉ xử lý *latest turn*, mang theo context các lượt trước, áp dụng correction (M01–M06).
- **Không gọi tool helper thừa** (xem 4.3) — chỉ gọi tool cần thiết để tránh `extra_tool_call`.

### 4.2 Làm rõ `tools.yaml` (A)

Trong `description` từng tool, viết rõ *khi nào dùng* + *quy ước args*:
map tên→handle ở `timeline`; `Top` vs `Latest` ở `social_search`; `news`+`day/week` ở `lookup`;
"chỉ dùng khi đã có URL" ở `fetch`; "dùng khi thiếu thông tin / xác nhận yes_no trước hành động ghi" ở `clarify`;
"chỉ gửi khi `confirmed=true`" ở `send`.

### 4.3 >3 tool mới (B) — chọn tool LOCAL, không cần thêm API key, build nhanh, test được

Mỗi tool: tạo `tools/<name>/tool.py` (hàm trả `dict`, bắt lỗi bằng `err()` trong `tools/_shared.py`) +
`tools/<name>/TOOL.md` (frontmatter theo `tools/README.md`) + thêm vào `TOOL_FUNCTIONS` trong `tools/__init__.py` +
khai báo trong `tools.yaml`. Đề xuất 4 tool:

| Tool mới | kind | Làm gì | Vì sao an toàn |
|---|---|---|---|
| `now` | control | Trả ngày/giờ hiện tại + map "hôm nay/tuần này"→timeframe | local, hỗ trợ reasoning thời gian |
| `handle_lookup` | local_knowledge | Map tên người nổi tiếng → twitter handle (dict cục bộ) | local, hỗ trợ routing |
| `save_digest` | action (`side_effect: local_file_write`) | Ghi digest markdown ra file cục bộ | action an toàn, không gọi mạng |
| `dedupe` | local_formatter | Gộp/loại trùng list item theo URL | local, formatter thuần |

> **⚠️ Rủi ro then chốt — `extra_tool_call`:** grader phạt tool gọi thừa. Tool mới phải mô tả **rất hẹp** để model KHÔNG gọi chúng trong các case base (vd đừng để `now` bị kích hoạt ở R03 "tin hôm nay"). Sau khi merge tool mới, **A phải chạy lại base eval** để chắc accuracy không tụt. Mỗi tool mới nên có group eval case riêng để chứng minh nó hoạt động.

> **Nếu rename tool:** phải đồng bộ tên ở `tools.yaml` ↔ `tools/__init__.py` ↔ `data/eval_base.json` + `data/eval_research_extension.json` (theo cảnh báo README), nếu không eval báo `not declared in tools.yaml`. **Khuyến nghị: KHÔNG rename** để tránh rủi ro.

### 4.4 10 group eval case (B) — 5 single + 5 multi

Định dạng theo `eval_base.json`: `id`, `phase:"B"`, `query` HOẶC `turns`, `failure_type` (trong `allowed_failure_types`:
`wrong_tool, wrong_arg_value, wrong_boundary, unnecessary_tool, out_of_scope, missing_info`),
`expect` (`tool_calls` hoặc `no_tool:true`), `metadata.what_it_tests`. Gợi ý:

- **Single (5):** (1) tweet của một người khác để test thêm map handle; (2) "top vs latest" biến thể khác; (3) out-of-scope khác (vd hỏi thời tiết) → `no_tool`; (4) case kích hoạt 1 tool mới (vd `save_digest`); (5) `lookup` general (không phải news) để phân biệt topic.
- **Multi (5):** (1) clarify→fill cho URL; (2) correction đổi chủ đề giữ timeframe; (3) đổi tool giữa chừng (social→web); (4) carry-over limit qua 2 lượt; (5) xác nhận yes_no rồi mới `send`.

### 4.5 UI Streamlit (C)

`ui/app.py`: chọn provider + version, ô nhập, gọi cùng agent loop như `chat.py`/`run_eval.py`
(import `ResearchAgent`, `make_provider`, `TOOL_FUNCTIONS`, load `system_prompt.md` + `tools.yaml`),
hiển thị: text trả lời + danh sách tool calls (tên + args) + kết quả tool. Thêm `streamlit` vào `requirements.txt`.
Chạy: `streamlit run ui/app.py`. (Một nửa điều kiện điểm thưởng.)

---

## 5. Checklist nộp bài (C chốt ở 2:45–3:00)

Lệnh chạy (từ `starter_v0/`):

```bash
python scripts/preflight_provider.py --provider openrouter
python run_eval.py --provider openrouter --version v0 --suite base  --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v1 --suite base  --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v2 --suite base  --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite base  --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
python chat.py     --provider openrouter --version v3
python scripts/parse_runs.py runs/ --output analysis/base_runs.csv   # tùy chọn
```

File phải có trong `starter_v0/` khi nộp:

- [ ] `artifacts/system_prompt.md` (đã viết lại)
- [ ] `artifacts/tools.yaml` (mô tả rõ ràng + tool mới đã khai báo)
- [ ] `artifacts/version_log.csv` có **đủ v0, v1, v2, v3** (kèm `prompt_hash`, `tools_hash`, `metric_before/after`, `run_file` lấy từ output)
- [ ] `artifacts/REPORT.md` điền đầy đủ (metrics, version evidence, failure analysis, team eval, live chat, bonus, reflection)
- [ ] `data/eval_group.json` có **≥10 case** (5 single + 5 multi)
- [ ] `runs/*.json` (tất cả version)
- [ ] `transcripts/*.transcript.json` (≥3 lượt live)
- [ ] `analysis/*.csv` (nếu có parse)
- [ ] Tool mới: `tools/<name>/tool.py` + `TOOL.md` + đăng ký trong `tools/__init__.py` (≥4 tool cho điểm thưởng)
- [ ] UI: `ui/app.py` + `streamlit` trong `requirements.txt`
- [ ] **KHÔNG commit `.env` / API key** (kiểm tra `.gitignore` + `git status`)
- [ ] Tên tool đồng bộ ở 3 nơi (nếu có rename); base eval không có `extra_tool_call` do tool mới

Sanity cuối: mở 1 run JSON v3, xác nhận `summary.case_accuracy` cao hơn v0; xác nhận `prompt_hash`/`tools_hash` v3 khác v0 (chứng tỏ thật sự có thay đổi).

---

## 6. Verification (kiểm tra từng đầu việc đã đúng)

- Chạy thử baseline v0 ra được run JSON → pipeline hoạt động trước khi tối ưu.
- Mỗi tool mới chạy được smoke-test:
  `python -c "from tools import TOOL_FUNCTIONS as T; print(T['<new_tool>'](...))"`
- `python run_eval.py ... --suite group --eval-cases data/eval_group.json` chạy không lỗi validate.
- `streamlit run ui/app.py` mở được và trả lời 1 request mẫu kèm hiển thị tool calls.
