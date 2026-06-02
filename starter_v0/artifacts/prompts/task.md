# Task — Phân Công Công Việc (so với `main`)

Branch `huyen` vs `main`: **21 file thay đổi** — 18 file mới đã commit (`3a9357a`), 3 file đã điền chưa commit (`REPORT.md`, `version_log.csv`, `eval_group.json`).

---

## M1 — Prompt & Optimization

Tối ưu prompt/tools qua v0→v3, kéo `case_accuracy` **0.65 → 1.0**.

| File                                        | Trạng thái      | Nội dung                                |
| ------------------------------------------- | --------------- | --------------------------------------- |
| `artifacts/system_prompt.md`                | sửa             | prompt cuối (v3)                        |
| `artifacts/prompts/system_prompt.v0→v3.md`  | mới (4 file)    | 4 phiên bản qua từng vòng               |
| `artifacts/prompts/tools.pre_keywords.yaml` | mới             | snapshot tools.yaml trước khi thêm tool |
| `artifacts/tools.yaml`                      | sửa             | mô tả routing + đăng ký `keywords`      |
| `runs/v0,v1,v2,v3_base*.json`               | mới (5)         | base eval: 0.65 → 0.85 → 0.85 → **1.0** |
| `artifacts/version_log.csv`                 | đã điền (v0–v3) | hash + metric trước/sau ✅              |

---

## M2 — Tooling & Eval

Viết tool mới + 10 eval case, chạy group/extension eval.

| File                                 | Trạng thái        | Nội dung                                     |
| ------------------------------------ | ----------------- | -------------------------------------------- |
| `tools/keywords/tool.py` + `TOOL.md` | mới               | **tool mới bắt buộc** (trích keyword cục bộ) |
| `tools/__init__.py`                  | sửa               | đăng ký `keywords` vào `TOOL_FUNCTIONS`      |
| `data/eval_group.json`               | đã điền (G01–G10) | 5 single + 5 multi turn ✅                   |
| `runs/v3_B_group_*.json` (×2)        | mới               | group eval **10/10**                         |
| `runs/v3_B_extension_*.json`         | mới               | extension eval 6/10 (`policy_area` sai)      |

---

## M3 — Chat, UI & Report

Chat live, UI Streamlit (bonus), viết report tổng hợp.

| File                                      | Trạng thái     | Nội dung                            |
| ----------------------------------------- | -------------- | ----------------------------------- |
| `app.py`                                  | mới (215 dòng) | **UI Streamlit** Live Trace (bonus) |
| `artifacts/poster.html`                   | mới (447 dòng) | poster Phần A để demo               |
| `transcripts/v3_openai_*.transcript.json` | mới            | chat live 4 lượt                    |
| `artifacts/REPORT.md`                     | đã điền        | report 2 phần A + B ✅              |

---

## Trạng thái nhiệm vụ

**Bắt buộc — đã đủ:** prompt v0–v3 (M1) · tool mới `keywords` (M2) · 10 eval case (M2) · version_log (M1) · transcript (M3) · REPORT (M3).

**Điểm thưởng — đạt:** UI `app.py` (M3) **+** tool mới `keywords` (M2).

**Còn lại:** commit 3 file đã điền (`REPORT.md`, `version_log.csv`, `eval_group.json`) lên branch `huyen`.
