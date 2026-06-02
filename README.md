# Day 04 Lab v2 — Research Agent Tool Eval

## Brief

Trong lab này, nhóm build một research agent nhỏ nhưng chạy thật. Agent nhận request của user, chọn tool, truyền arguments, chạy tool thật, lưu full JSON log, rồi dùng log đó để tối ưu prompt/tool declaration qua nhiều version.

Điều cần học không phải là "chatbot trả lời hay". Điều cần học là vòng lặp evidence-driven:

1. Chạy baseline bằng API thật.
2. Đọc run JSON để biết sai tool, sai args, thiếu hỏi lại, hoặc gọi tool thừa.
3. Sửa `artifacts/system_prompt.md` hoặc `artifacts/tools.yaml`.
4. Chạy lại và ghi versioning.
5. Tự viết thêm eval case để đo những lỗi nhóm quan tâm.
6. Viết report dựa trên log thật, không dựa vào cảm giác.

## Scope

Nhiệm vụ bắt buộc:

- Setup chạy được bằng provider thật.
- Agent có ít nhất 5 tool trong `artifacts/tools.yaml`.
- Chạy base eval.
- Tối ưu ít nhất 3 vòng sau baseline: `v1`, `v2`, `v3`.
- Ghi `artifacts/version_log.csv`.
- Viết thêm ít nhất 1 tool mới (kèm `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml`).
- Tự viết thêm 10 eval case vào `data/eval_group.json`, trong đó 5 single turn và 5 multi turn.
- Nộp run JSON, transcript JSON, report.
- Bắt buộc có UI chạy được bằng Streamlit hoặc Vercel.
- Hoàn thành `artifacts/REPORT.md`: Phần A (giới thiệu agent: tool gì, làm được gì, câu hỏi mẫu) xong **trước 16:30** làm tài liệu phụ trợ khi demo; Phần B (chi tiết) hoàn thiện sau để nộp bài.

Bonus:

- Action tool `send`: có confirmation trước khi gửi.
- Extra tools: `policy`, `papers`, `paper_text`.


**Điểm thưởng (bonus point):** team nào làm **CẢ HAI** — dựng được UI **và** tự viết thêm hơn 3 tool mới (ngoài các tool có sẵn, kèm `TOOL.md` + đăng ký trong `tools/__init__.py` + `tools.yaml`) — sẽ được cộng điểm thưởng.

## Folder Map

```text
starter_v0/
  agent.py                    # one-shot model -> tool calls -> tool execution
  chat.py                     # interactive chat, multi-round tools, transcript JSON
  run_eval.py                 # eval routing + args, writes runs/*.json
  versioning.py               # prompt/tool hash
  artifacts/
    system_prompt.md          # student edits
    tools.yaml                # student edits
    version_log.csv           # student fills
    REPORT.md                 # report: Phần A debate poster + Phần B chi tiết
  data/
    eval_base.json            # fixed base eval, do not edit the cases
    eval_group.json           # team adds at least 5 cases
    eval_research_extension.json
  tools/
    README.md                 # tool folder contract
    <tool_name>/
      TOOL.md                 # frontmatter + notes
      tool.py                 # self-contained implementation
  company_policy/             # local markdown KB for bonus policy tool
  providers/                  # OpenRouter/OpenAI/Anthropic/Gemini adapters
  scripts/preflight_provider.py
  samples/                    # mock format examples (transcript, run-analysis, version_log)
```

## Tool Tracks

Phần mô tả dưới đây tóm tắt mỗi tool *làm gì*. Việc xác định *khi nào dùng* tool nào là phần nhóm tự định nghĩa trong prompt và tool declaration.

Core tools:

- `clarify`: gửi một câu hỏi cho người dùng và chờ lượt trả lời tiếp theo.
- `timeline`: lấy bài đăng gần đây của một tài khoản (`screenname`).
- `social_search`: tìm bài đăng theo từ khóa (`search_type`: Latest/Top).
- `lookup`: tìm trên web (có `topic` general/news và `timeframe`).
- `fetch`: đọc nội dung một URL.
- `format`: trình bày các item đã có thành markdown digest.

Bonus tools:

- `send`: gửi text lên Telegram channel (chỉ gửi khi `confirmed=true`).
- `policy`: tìm trong company policy markdown nội bộ.
- `papers`: tìm paper trên arXiv.
- `paper_text`: tải PDF arXiv và trích text cục bộ.

Mỗi tool nằm trong thư mục riêng dưới `starter_v0/tools/<tool_name>/`.

## ⚠️ Nếu nhóm đổi tên tool: phải đồng bộ

Eval chấm theo **đúng tên tool**. Nếu nhóm đổi tên một tool cho rõ nghĩa hơn (ví dụ `send` → `send_telegram`), **phải đổi đồng bộ ở CẢ những nơi sau**, nếu không eval báo lỗi `not declared in tools.yaml` hoặc chấm sai mọi case:

1. `artifacts/tools.yaml` — field `name`
2. `tools/__init__.py` — key trong `TOOL_FUNCTIONS`
3. `data/eval_base.json` **và** `data/eval_research_extension.json` — `expect.tool_calls[].name`

(Không cần đổi tên hàm trong `tools/<folder>/tool.py` — chỉ cần key trỏ đúng hàm. Không sửa *nội dung case* trong `eval_base.json`, chỉ đổi tên tool nếu nhóm rename.)

## Setup

Run from `starter_v0/`:

```bash
cd starter_v0
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env`. Minimum recommended:

```bash
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...
FIRECRAWL_API_KEY=...
RAPIDAPI_KEY=...
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
```

Tool setup details are in [TOOL-SETUP.md](TOOL-SETUP.md).

Preflight:

```bash
python scripts/preflight_provider.py --provider openrouter
```

If preflight fails, fix provider key, dependency, or network before running eval.

## Step 1 — Run Baseline

Run the fixed base eval as `v0`:

```bash
python run_eval.py \
  --provider openrouter \
  --version v0 \
  --suite base \
  --eval-cases data/eval_base.json
```

Output is saved to `runs/*.json`. Read:

- `summary.case_accuracy`
- `summary.tool_routing_accuracy`
- `summary.argument_accuracy`
- `summary.multiturn_accuracy`
- `results[*].result.failures`
- `results[*].result.observed_mismatch`

The run JSON also stores `artifact_version`, `prompt_hash`, `tools_hash`, actual tool calls, and actual tool results. That is the evidence for your report.

Optional: parse run JSON into a flat CSV table for analysis:

```bash
python scripts/parse_runs.py runs/ --output analysis/base_runs.csv
```

## Step 2 — Fix One Thing

Edit only:

- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`

Do not edit the cases in `data/eval_base.json`.

Method, not memorized answers:

1. Mở run JSON. Với mỗi case FAIL, đọc `observed_mismatch` + `failures` + `actual_tool_calls`.
2. Đặt một giả thuyết: *vì sao* agent chọn sai (thiếu rule routing? thiếu convention args? prompt đang khuyến khích đoán/gửi/làm-một-bước?).
3. Sửa **một** thứ (một dòng prompt hoặc một description) để kiểm chứng giả thuyết đó.
4. Chạy lại, so metric trước/sau. Nếu không cải thiện, đổi giả thuyết.

Đổi một giả thuyết mỗi lần để version log có ý nghĩa.

## Step 3 — Run 3 Optimization Versions

Run at least three improved versions:

```bash
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
```

After each run, fill `artifacts/version_log.csv`:

```text
version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_before,metric_after,run_file
```

Use hashes and run file paths from the eval output.

## Step 4 — Add Team Eval

Add at least 5 cases to `data/eval_group.json`.

Each case needs:

- `id`
- `phase`: always `"B"`
- `query` or `turns`
- `failure_type`: one of `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`
- `expect`: `tool_calls` or `no_tool`
- `metadata.what_it_tests`

Run:

```bash
python run_eval.py \
  --provider openrouter \
  --version v3 \
  --suite group \
  --eval-cases data/eval_group.json
```

Optional extension eval:

```bash
python run_eval.py \
  --provider openrouter \
  --version v3 \
  --suite extension \
  --eval-cases data/eval_research_extension.json
```

## Step 5 — Chat Live

`chat.py` is for live multi-round interaction. It logs every turn to `transcripts/*.transcript.json`.

```bash
python chat.py --provider openrouter --version v3
```

Try at least 3 live turns, for example:

- A normal research request.
- A request thiếu thông tin (không nói rõ account/URL), rồi lượt sau bổ sung.
- Một request "đăng/gửi bản tin lên Telegram" — quan sát agent có hành động ngay hay hỏi lại trước, rồi tự quyết định hành vi nào mới đúng và sửa prompt cho khớp.

## Deploy nhanh để team khác dùng thử (khuyến nghị: Cloudflare Tunnel)

Để team cùng zone tự thử agent trong Team showdown, expose UI đang chạy local ra một link public. Cách nhanh nhất, không cần đăng ký domain hay deploy lên cloud, là **Cloudflare Tunnel** (`cloudflared`).

1. Chạy UI local trước (ví dụ Streamlit mặc định cổng `8501`):

   ```bash
   streamlit run app.py            # → http://localhost:8501
   ```

2. Cài `cloudflared`:

   ```bash
   brew install cloudflared                          # macOS
   winget install --id Cloudflare.cloudflared        # Windows (hoặc: scoop install cloudflared)
   # Linux: xem https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
   ```

   Windows: nếu báo `cloudflared not recognized`, mở terminal mới rồi chạy lại.

3. Mở tunnel trỏ vào cổng UI — lệnh trả về ngay một URL `https://<random>.trycloudflare.com`:

   ```bash
   cloudflared tunnel --url http://localhost:8501
   ```

4. Copy URL đó, dán vào `REPORT.md` Phần A (mục "Link dùng thử") để team khác mở thử.

Lưu ý: link `trycloudflare.com` là tạm thời, sống theo phiên `cloudflared` (tắt lệnh là mất). Giữ lệnh chạy trong suốt buổi showdown. Nếu team deploy hẳn lên Vercel/Streamlit Cloud thì dùng link đó thay cho tunnel.

## Step 6 — Report + Debate Poster

Hoàn thành `artifacts/REPORT.md`. File này có 2 phần với deadline khác nhau:

- **Phần A — Giới thiệu agent** (ngắn gọn 1 trang) — **phải xong trước 16:30**, làm tài liệu phụ trợ để team khác hiểu nhanh khi demo. Chỉ cần: (1) agent làm được gì, (2) agent có những tool gì và mỗi tool làm được gì, (3) vài câu hỏi mẫu để team khác tự thử.
- **Phần B — Chi tiết / Bằng chứng** — **có thể hoàn thiện sau Team showdown để nộp bài**. Bảng đầy đủ v0–v3, failure analysis, eval cases, live chat, reflection — dựa trên log thật (run JSON, version_log).

**Format Phần A:** nộp tối thiểu bản markdown trong `REPORT.md`. Khuyến khích biến Phần A thành **poster HTML/SVG 1 trang** để show trực tiếp cho team cùng zone (ví dụ `artifacts/poster.html` hoặc `artifacts/poster.svg`) — cùng nội dung, dễ nhìn hơn. Poster HTML/SVG là tùy chọn, không thay thế bản markdown.

## Submit

Submit `starter_v0/` with:

- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`
- `artifacts/version_log.csv` with at least `v0`, `v1`, `v2`, `v3`
- `artifacts/REPORT.md` (Phần A debate poster — xong trước 16:30; Phần B chi tiết — nộp sau)
- `artifacts/poster.html` hoặc `artifacts/poster.svg` nếu team làm poster để debate (tùy chọn)
- `data/eval_group.json` with at least 5 team cases
- `runs/*.json`
- `analysis/*.csv` if you parsed run logs
- `transcripts/*.transcript.json`
- code changes if your team added or changed tools/UI

Do not submit `.env` or API keys.

## Checkpoint 4h

- 15:00 - Run baseline + build UI
- 15:30 - Improve prompt/tools for v1 + build at least 1 tool
- 16:00 - Write team eval cases + improve v2
- 16:30 - Team showdown (demo sản phẩm; REPORT.md Phần A / poster là tài liệu phụ trợ để team khác hiểu nhanh agent có tool gì, làm được gì)
- 17:30 - Improve v3 + hoàn thiện report Phần B
