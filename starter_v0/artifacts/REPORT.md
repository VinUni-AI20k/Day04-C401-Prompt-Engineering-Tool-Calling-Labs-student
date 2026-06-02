# Day 04 Lab v2 Report - Research Agent

## Team

- Team: `Nhóm 4`
- Members: `Phạm Ngọc Vinh - 2A202600563, Nguyễn Huy Bảo - 2A202600997, Phan Quốc Anh - 2A202600890`
- Provider/model: Gemini - `gemini-3.1-flash-lite`
- PUBLIC UI: `https://labai.xn--ngcvinh-dx4c.vn/`

---

# PHAN A - Gioi thieu agent

## A1. Agent nay lam duoc gi

Research Agent cua nhom dung de route dung tool cho cac tac vu research: tim tin web, tim tweet theo tai khoan/chu de, doc URL, tim paper arXiv, tra cuu policy noi bo, format digest, va gui Telegram khi da co xac nhan. Agent duoc toi uu bang eval log that qua cac version `v0` -> `v3`, voi ket qua base eval moi nhat dat 20/20.

**Link dung thu (local):**

URL: `http://127.0.0.1:8686`

Neu can public demo, co the deploy bang Cloudflare Tunnel/Vercel/Streamlit Cloud va thay URL local bang URL public.

## A2. Tool agent co

| Ten tool | Lam duoc gi | Tool moi nhom them? |
|---|---|---|
| clarify | Hoi lai nguoi dung khi thieu handle, URL, paper ID, hoac can xac nhan hanh dong gui/post/publish | khong |
| timeline | Lay tweet/post gan day cua mot tai khoan cu the, vi du `sama`, `elonmusk`, `karpathy` | khong |
| social_search | Tim tweet/post theo chu de tren Twitter/X, ho tro `Latest` va `Top` | khong |
| lookup | Tim kiem web, dac biet cho tin tuc/current events voi `topic=news` va `timeframe` | khong |
| fetch | Doc/scrape mot URL cu the do nguoi dung cung cap | khong |
| format | Format cac item da co thanh markdown digest | khong |
| send | Gui noi dung len Telegram, chi chay sau khi nguoi dung xac nhan | khong |
| policy | Tra cuu tai lieu company policy noi bo | khong |
| papers | Tim paper tren arXiv theo topic | khong |
| paper_text | Tai PDF arXiv va trich text khi co arXiv ID/URL | khong |

## A3. Cau hoi mau de thu

1. `Tweet mới nhất của Sam Altman là gì?`
2. `Tin tức AI hôm nay có gì nổi bật?`
3. `Tóm tắt bài này hộ mình: https://openai.com/blog/gpt-5`
4. `Cho mình các tweet phổ biến nhất về OpenAI`
5. `Gửi tin nhắn hello qua Telegram cho tôi`

---

# PHAN B - Chi tiet / Bang chung

## B1. Version Evidence

Bang duoi duoc lay tu `artifacts/version_log.csv` va `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Do prompt/tools ban dau co tinh mo ho, dung baseline de do cac loi routing, missing info va send boundary. | - | 0.60 | `runs/v0_B_base_gemini_20260602T144003498658.json` |
| v1 | `system_prompt.md`; `tools.yaml` | Mo ta tool ro hon va prompt co rule routing/missing-info/publish-boundary se giam wrong tool va missing-info. | 0.60 | 0.85 | `runs/v1_B_base_gemini_20260602T145712013136.json` |
| v2 | `system_prompt.md`; `tools.yaml` | Bat buoc `clarify.response_type` se sua loi model goi dung `clarify` nhung thieu/sai arg. | 0.85 | 0.95 | `runs/v2_B_base_gemini_20260602T145930465665.json` |
| v3 | `system_prompt.md`; `tools.yaml` | Them rule tieng Viet cho Telegram/post/publish de ep `response_type=yes_no` truoc khi gui. | 0.95 | 1.00 | `runs/v3_B_base_gemini_20260602T160835152753.json` |

**Latest v3 summary:**

```text
total_cases: 20
measured_cases: 20
provider_error_cases: 0
passed_cases: 20
case_accuracy: 1.0
tool_routing_accuracy: 1.0
argument_accuracy: 1.0
multiturn_accuracy: 1.0
```

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool / wrong_arg_value | `lookup(query="AI news today", topic="news")` | Tool name dung nhung query khong canonical va thieu `timeframe=day`. | Them convention trong prompt/tools: "hôm nay/today" -> `topic=news`, `timeframe=day`, query ngan gon nhu `AI`. |
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2...")` | Prompt cu khuyen khich dung tool moi khi can hanh dong, nen dung tool cho cau ngoai scope. | Them rule: khong dung tool cho math/coding/meta; out-of-scope thi answer/refuse without tool. |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | Agent doan Sam Altman khi nguoi dung khong noi tai khoan. | Them rule: thieu handle/account thi goi `clarify(response_type="text")`, khong doan. |
| R11_missing_url | missing_info | `lookup(query="tóm tắt bài viết mới nhất...")` | Agent doan bai viet khi nguoi dung noi "bai nay" nhung khong dua URL. | Them rule: thieu URL thi goi `clarify(response_type="text")`; `fetch` chi dung khi co URL. |
| R12_confirm_before_send | wrong_boundary | `send(...)` hoac `clarify(response_type="text")` | Action gui Telegram can confirmation yes/no truoc, nhung agent gui ngay hoac hoi noi dung. | Them publish boundary: moi send/post/publish phai `clarify(response_type="yes_no")` truoc, ke ca noi dung chua ro. |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | `lookup(query="AI news today")`, `social_search(query="AI")` | Da goi 2 tool nhung query web khong canonical. | Them rule request can 2 nguon thi goi ca 2 tool, va query web ngan gon `AI`. |
| M02_carryover_timeframe | wrong_arg_value | `lookup(query="latest robotics news today")` | Multi-turn carry dung timeframe nhung query khong canonical. | Them multi-turn rule: carry timeframe/topic, latest correction override, query ngan gon `robotics`. |
| M06_switch_tool | wrong_tool / wrong_arg_value | `lookup(query="OpenAI news", topic="news", timeframe="week")` | Switch tu Twitter sang web dung, nhung query/the timeframe khong toi uu. | Them rule "bo Twitter/chuyen sang web" -> `lookup`, giu topic `OpenAI`, news topic, query canonical. |

## B3. Team Eval Cases

`data/eval_group.json` hien tai van chua co case tu nhom:

```text
cases: []
```

Can bo sung 10 case theo yeu cau lab: 5 single-turn va 5 multi-turn. Bang duoi de team dien sau khi them va chay group eval.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `<dien case id>` | `<dien noi dung test>` | `<expected tool/no_tool>` | `<PASS/FAIL + run file>` |
| `<dien case id>` | `<dien noi dung test>` | `<expected tool/no_tool>` | `<PASS/FAIL + run file>` |
| `<dien case id>` | `<dien noi dung test>` | `<expected tool/no_tool>` | `<PASS/FAIL + run file>` |

## B4. Live Chat Evidence

Bang nay lay tu `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| `ui_gemini_20260602T153104840196`, turn 1 | `lấy cho tôi một bài viết liên quan đến công nghệ ai mới nhất` | `lookup` | Gemini `gemini-3.1-flash-lite`; UI transcript | Agent route sang web lookup cho yeu cau research/news. |
| `ui_gemini_20260602T153558961429`, turn 1 | `Tin tức AI hôm nay có gì nổi bật?` | `lookup`, `format` | v3-style routing; UI transcript | Agent lay tin AI va format thanh digest. |
| `ui_gemini_20260602T155641041416`, turn 1 | `cho tôi một vài thông tin chính sách nội bộ` | `policy` | UI transcript | Agent dung local company policy KB thay vi web search. |
| `ui_gemini_20260602T155641041416`, turn 2 | `tải pdf paper mới nhất về AI` | `papers` | UI transcript | Agent route sang arXiv paper search. |
| `ui_gemini_20260602T160013877452`, turn 1-2 | `gửi tin nhắn hello qua telegram cho tôi` -> `có` | `clarify`, sau do `send` | UI transcript + Telegram guardrail | Agent khong gui ngay; hoi xac nhan truoc khi goi send. |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tools/send/tool.py`, UI transcripts | Tool chi gui khi `confirmed=true`; prompt bat buoc `clarify(response_type=yes_no)` truoc action gui/post/publish. | Can `TELEGRAM_BOT_TOKEN` va `TELEGRAM_CHAT_ID` dung. Da sua error handling de khong lo token trong URL loi. |
| arXiv/company policy | `tools/papers/tool.py`, `tools/paper_text/tool.py`, `tools/policy/tool.py` | Tim paper arXiv, tai text paper khi co ID/URL, tra cuu policy noi bo bang local markdown. | arXiv co rate limit nen tool co sleep/retry nhe; policy docs la untrusted content nen tool tra `trust_boundary`. |
| UI | `ui_server.py`, `transcripts/*.transcript.json` | UI local ho tro provider/model/version, chat, inspector tool calls/results, transcript logging, Enter-to-send va Shift+Enter xuong dong. | UI chay local; can restart server sau khi sua `.env`. |

## B6. Reflection

- Fix thuoc `system_prompt.md`: routing rules, missing-info behavior, multi-turn carryover/correction, out-of-scope boundary, publish/send confirmation boundary, canonical argument conventions.
- Fix thuoc `tools.yaml`: mo ta tool ro hon de model phan biet `timeline` vs `social_search`, `lookup` vs `fetch`, `clarify` vs `send`; bat buoc `clarify.response_type`; mo ta `send` nhu external write action.
- Failure can manual review: Telegram send can pass routing eval nhung van fail runtime neu `TELEGRAM_CHAT_ID` sai hoac bot chua co quyen. Vi vay can test live voi Telegram API, khong chi dua vao eval routing.
- Cai tien tiep theo: them 10 group eval cases, them tool moi theo yeu cau lab neu can diem toi da, viet UI public deploy, va them health/status panel cho Telegram/Tavily/Firecrawl/RapidAPI key.
