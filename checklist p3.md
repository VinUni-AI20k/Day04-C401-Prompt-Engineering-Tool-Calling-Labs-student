# Checklist hoàn thành công việc — Người 3 (Eval & Report Lead)

Tick hết các mục là phần của P3 đạt chuẩn **điểm cao**. Mỗi mục kèm điều kiện *"xong khi nào"* (Definition of Done), kiểm chứng được — không phải cảm tính.

---

## 1. Eval cases — `data/eval_group.json` (deliverable bắt buộc)

- [ ] File đặt đúng `starter_v0/data/eval_group.json`, JSON **parse được** (không lỗi cú pháp).
- [ ] Đủ **≥10 case**: **5 single-turn** (có `query`) + **5 multi-turn** (có `turns`).
- [ ] Phủ **đủ 6 `failure_type`**: `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`.
- [ ] Mỗi case có đủ field: `id`, `phase:"B"`, (`query` HOẶC `turns`), `failure_type` hợp lệ, `expect` (`tool_calls[...]` hoặc `no_tool:true`), `metadata.what_it_tests`.
- [ ] Mọi tên tool trong `expect.tool_calls[].name` đều **declared trong `tools.yaml`** *và* **implemented trong `tools/`** → chạy validate **0 error**.
- [ ] Có vài case `difficulty:hard` (eval đủ khó → cho thấy nhóm hiểu sâu, không chỉ case dễ).

> Kiểm tra nhanh trước khi tốn token API: chạy snippet validate ở **P3_RUNBOOK bước A** → phải in `10 cases`, `multi: 5`, đủ 6 type, `PASS`.

## 2. Chạy eval & thu thập log (`runs/`, `analysis/`)

- [ ] Đã chạy `--suite group` trên `eval_group.json` với artifact **v3 mới nhất của P1** → có `runs/v3_B_group_*.json`.
- [ ] Đã chạy `--suite extension` trên `eval_research_extension.json` → có `runs/v3_B_extension_*.json`.
- [ ] Mỗi run file đọc được: `summary.case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy`.
- [ ] Đã parse toàn bộ runs → `analysis/all_runs.csv` (có cột `passed`, `observed_mismatch`, `failures`).
- [ ] **Không có case `provider_error`** (nếu có → fix key/network rồi chạy lại, đừng để lẫn vào số liệu báo cáo).

## 3. Chat live (`transcripts/`)

- [ ] Đã chạy `chat.py` với **≥3 lượt** thật → có `transcripts/*.transcript.json`.
- [ ] Đủ 3 kịch bản: (a) research bình thường · (b) thiếu info → bổ sung lượt sau · (c) yêu cầu đăng Telegram (quan sát agent **hỏi xác nhận trước** khi gửi).
- [ ] Transcript ghi đủ tool calls từng lượt (để dẫn chứng trong REPORT).

## 4. REPORT — `artifacts/REPORT.md` (phần chấm nặng nhất)

- [ ] **Team**: điền đủ tên nhóm, 3 thành viên, provider/model.
- [ ] **Final Metrics**: số liệu lấy đúng từ `runs/*.json`, có dẫn tên run file.
- [ ] **Version Evidence**: bảng v0→v3, mỗi version 1 hypothesis + metric_before/after, **khớp `version_log.csv` của P1**.
- [ ] **Failure Analysis**: dùng `failures` thật từ log (không mô tả chung chung).
- [ ] **Team Eval Cases**: cột Result điền từ run group (bảng 10 case đã có sẵn what-it-tests).
- [ ] **Live Chat Evidence**: dẫn từ transcript ở mục 3.
- [ ] **Reflection**: trả lời đủ 4 câu hỏi.
- [ ] ⚠️ **Mọi con số trong REPORT khớp với run file** — không bịa, không làm tròn sai. Đây là tiêu chí "evidence-driven" cốt lõi của bài.

## 5. Bonus (chỉ nếu nhóm làm — để ăn bonus point)

- [ ] Nếu P2 làm UI + ≥4 tool mới → điền mục **Bonus Evidence** (file dẫn chứng + guardrail).
- [ ] Nếu tool bonus (`send`/`policy`/`papers`/`paper_text`) chạy được → dẫn run/transcript chứng minh.

## 6. Phối hợp & đồng bộ (tránh lỗi phút chót)

- [ ] **Tên tool đã chốt với P1/P2** trước khi chạy group eval — nếu rename, `expect` trong file của mình phải khớp `tools.yaml`, nếu không eval báo `not declared`.
- [ ] Chạy group/extension eval **sau khi P1 chốt v3** (để `artifact_version` trong run file đúng).
- [ ] `version_log.csv` (P1) đã đủ `v0,v1,v2,v3` trước khi mình chốt REPORT.

## 7. Đóng gói & nộp bài (sanity check cuối)

- [ ] Bài nộp có đủ: `data/eval_group.json` · `runs/*.json` (group + extension) · `analysis/all_runs.csv` · `transcripts/*.transcript.json` · `artifacts/REPORT.md`.
- [ ] ❌ **KHÔNG** có `.env` hoặc API key trong bài nộp. Kiểm tra lại:
  ```bash
  grep -rIn -e "tvly-" -e "fc-" -e "sk-" -e "RAPIDAPI_KEY" \
    --include=*.md --include=*.json --include=*.csv . | grep -v ".env.example"
  ```
  (Không in ra dòng nào = an toàn.)
- [ ] Mở lại run file + REPORT lần cuối: số liệu nhất quán, mọi tên file được dẫn đều **tồn tại thật**.

---

### Tóm tắt "đạt vs xuất sắc"

| Mức | Điều kiện |
|---|---|
| **Đạt (đủ điểm phần P3)** | 10 case PASS validation · chạy group+extension · ≥3 transcript · REPORT điền đủ, số khớp log |
| **Xuất sắc (kéo điểm cao)** | Eval có case `hard` cover góc lạ (format routing, confirmed=true, timeframe year/month, latest-turn meta) · Failure Analysis chỉ rõ fix thuộc prompt hay tools.yaml · REPORT phản ánh đúng vòng evidence-driven v0→v3 |