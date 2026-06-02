# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Debate Poster**: 1 trang để trình bày trong buổi debate (Team showdown). **Xong trước 16:30.** Team khác đọc 2 phút là hiểu nhóm bạn cải thiện gì, thêm tool gì, vì sao tin là đúng. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, chat). **Có thể hoàn thiện sau buổi debate để nộp bài.**
>
> Cả hai phần phải dựa trên log thật (run JSON, version_log), không phải cảm tính.

## Team

- Team:
- Members:
- Provider/model:

---

# PHẦN A — Debate Poster

## A1. Một dòng tóm tắt

> 1 câu: nhóm đã làm gì để kéo điểm lên.

Ví dụ: "Thêm rule routing rõ ràng + map tên người → handle trong `tools.yaml`, đưa `case_accuracy` từ 0.65 → 0.90."

## A2. Kết quả (baseline → final)

| Metric | Baseline (v0) | Final (v?) | Δ |
|---|---:|---:|---:|
| case_accuracy | 0.65 |  |  |
| tool_routing_accuracy |  |  |  |
| argument_accuracy |  |  |  |
| multiturn_accuracy |  |  |  |

- Run file baseline:
- Run file final:
- Group eval run file / accuracy:

## A3. Ba thay đổi quan trọng nhất

> Mỗi dòng: *triệu chứng trong log* → *giả thuyết* → *sửa gì* → *kết quả*. Tối đa 3. (Bảng v0–v3 đầy đủ ở Phần B.)

| # | Lỗi quan sát trong log | Sửa ở đâu (`prompt`/`tools.yaml`) | Kết quả (case nào pass thêm) |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

## A4. Tool mới nhóm tự thêm

> Lab bắt buộc thêm ít nhất 1 tool mới. (Bonus khác — UI, telegram, arXiv — ở Phần B.)

| Tên tool | Tool làm gì | Vì sao cần (lỗi/khoảng trống nào) | Args chính | Có confirmation? |
|---|---|---|---|---|
|  |  |  |  |  |

- File tool: `tools/<tên>/tool.py` + `tools/<tên>/TOOL.md`
- Đã đăng ký ở: `tools/__init__.py` ☐  `tools.yaml` ☐
- (Nếu rename tool có sẵn) đã đồng bộ 4 nơi: ☐ tools.yaml ☐ __init__.py ☐ eval_base.json ☐ eval_research_extension.json

## A5. Một bằng chứng before/after (để cãi)

> Chọn 1 case mạnh nhất. Dán đoạn log thật, không mô tả cảm tính. (Bảng failure đầy đủ ở Phần B.)

- Case ID:
- Request:

**Trước (v0):**
```
actual_tool_calls: ...
observed_mismatch: ...
```

**Sau (final):**
```
actual_tool_calls: ...
```

## A6. Eval case nhóm tự viết — và vì sao nó đáng

> Chọn 1–2 case nhóm tự hào nhất. Nó bắt được lỗi gì mà eval_base bỏ sót? (Danh sách đủ 10 case ở Phần B.)

| Case ID | Bắt lỗi loại gì (`failure_type`) | Vì sao case này khó / đáng tranh luận |
|---|---|---|
|  |  |  |

## A7. Quan điểm mang ra debate

> 1 câu khẳng định nhóm sẵn sàng bảo vệ trước team khác. Phải có thể bị phản biện.

Ví dụ: "Action tool nên LUÔN hỏi xác nhận trước khi gửi, kể cả khi user đã nói rõ — vì cost của gửi nhầm > cost của 1 câu hỏi."

Khẳng định của nhóm:

## A8. Câu hỏi mở cho các team khác

> 1 câu hỏi nhóm chưa tự trả lời được — để mời tranh luận.

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
