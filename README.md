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

Bonus:

- Action tool `send`: có confirmation trước khi gửi.
- Extra tools: `policy`, `papers`, `paper_text`.
- UI: Streamlit hoặc Vercel.

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
    REPORT.md                 # final report template
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

## Hướng dẫn cài đặt, setup, chạy demo

Dưới đây là các bước để cài đặt môi trường, thiết lập API keys và chạy demo (bao gồm giao diện Streamlit). Các lệnh bên dưới chạy từ thư mục gốc repo, sau đó chuyển vào `starter_v0/` để chạy agent.

### 1. Chuẩn bị môi trường

Yêu cầu:

- Python 3.10+.
- API key cho provider model, khuyến nghị `OPENROUTER_API_KEY`.
- API key cho các tool web/social nếu muốn chạy đầy đủ: `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY`.

Tạo virtual environment và cài dependencies:

```bash
cd starter_v0
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Trên Windows PowerShell:

```powershell
cd starter_v0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### 2. Cấu hình API keys

Mở file `starter_v0/.env` và điền các key cần dùng. Cấu hình tối thiểu khuyến nghị:

```bash
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...
FIRECRAWL_API_KEY=...
RAPIDAPI_KEY=...
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
```

Không commit `.env` hoặc API key vào repo.

Chi tiết setup từng tool nằm trong [TOOL-SETUP.md](TOOL-SETUP.md).

### 3. Kiểm tra provider trước khi chạy

Chạy preflight để xác nhận provider key, dependency và network đã sẵn sàng:

```bash
python scripts/preflight_provider.py --provider openrouter
```

Nếu preflight fail, sửa provider key, dependency hoặc network trước khi chạy eval.

### 4. Chạy demo nhanh

Chạy baseline eval với bộ case có sẵn:

```bash
python run_eval.py \
  --provider openrouter \
  --version v0 \
  --suite base \
  --eval-cases data/eval_base.json
```

Sau khi chạy xong, mở file JSON mới trong `starter_v0/runs/` để xem:

- `summary.case_accuracy`
- `summary.tool_routing_accuracy`
- `summary.argument_accuracy`
- `summary.multiturn_accuracy`
- `results[*].result.failures`
- `results[*].result.observed_mismatch`
- `results[*].actual_tool_calls`

Có thể parse run JSON thành CSV để phân tích dễ hơn:

```bash
python scripts/parse_runs.py runs/ --output analysis/base_runs.csv
```

### 5. Chạy chat demo tương tác

Dùng `chat.py` để thử agent ở chế độ multi-turn thật:

```bash
python chat.py --provider openrouter --version v0
```

Gợi ý demo:

- Hỏi một research request bình thường, ví dụ tìm tin/bài viết gần đây theo chủ đề.
- Hỏi thiếu thông tin, ví dụ chỉ nói "xem timeline giúp mình" nhưng không đưa account, để kiểm tra agent có gọi `clarify` không.
- Thử request cần action, ví dụ nhờ gửi bản tin lên Telegram, để kiểm tra tool `send` có yêu cầu confirmation trước khi gửi không.

Transcript của phiên chat được lưu trong `starter_v0/transcripts/*.transcript.json`.

### 6. Chạy demo bằng Streamlit UI

Giao diện Streamlit cho phép bạn tương tác với Agent một cách trực quan, theo dõi các bước gọi tool và kết quả trả về. Sau khi đã cài dependencies và cấu hình `.env`, chạy:

```bash
cd starter_v0
streamlit run streamlit_app.py
```

Trên Windows PowerShell, chạy trong thư mục `starter_v0/` sau khi activate `.venv`:

```powershell
streamlit run streamlit_app.py
```

Mở URL Streamlit hiển thị trên terminal, thường là:

```text
http://localhost:8501
```

Trong sidebar của UI:

- Chọn provider, ví dụ `openrouter`.
- Nhập version muốn demo, ví dụ `v0` hoặc `v3`.
- Để trống `Model override` nếu muốn dùng model mặc định của provider.
- Điều chỉnh `History window` và `Max tool rounds` nếu cần test multi-turn dài hơn.

Gợi ý test trên UI:

- Hỏi một research request bình thường để xem agent chọn tool và trả lời.
- Hỏi thiếu thông tin để kiểm tra agent có yêu cầu clarification.
- Mở phần expander của từng lượt để xem `Tool calls` và `Tool results`.
- Bấm `Reset chat` khi đổi provider/version để transcript mới dùng đúng cấu hình.

Transcript của Streamlit demo được lưu trong `starter_v0/transcripts/*.transcript.json`.

### 7. Vòng lặp làm lab

Sau demo, workflow chính là:

1. Chạy eval baseline `v0`.
2. Đọc run JSON để tìm lỗi routing, args, boundary hoặc multi-turn.
3. Sửa `artifacts/system_prompt.md` hoặc `artifacts/tools.yaml`.
4. Chạy lại với `v1`, `v2`, `v3`.
5. Ghi kết quả từng vòng vào `artifacts/version_log.csv`.
6. Thêm case của nhóm vào `data/eval_group.json` và chạy suite `group`.

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

## Submit

Submit `starter_v0/` with:

- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`
- `artifacts/version_log.csv` with at least `v0`, `v1`, `v2`, `v3`
- `artifacts/REPORT.md`
- `data/eval_group.json` with at least 5 team cases
- `runs/*.json`
- `analysis/*.csv` if you parsed run logs
- `transcripts/*.transcript.json`
- code changes if your team added or changed tools/UI

Do not submit `.env` or API keys.

## Timeline 4h

- 0:00-0:25 setup, keys, preflight.
- 0:25-0:55 run baseline, inspect JSON.
- 0:55-1:45 improve prompt/tools for v1-v2.
- 1:45-2:15 write team eval cases.
- 2:15-2:45 run v3 + group eval.
- 2:45-3:20 chat live + transcript.
- 3:20-3:50 report.
- 3:50-4:00 package and final sanity check.
