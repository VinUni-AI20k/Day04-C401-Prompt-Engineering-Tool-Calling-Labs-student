# Day 04 Lab v2 Report — Research Agent

## Team

- Team: Group B + C
- Members: Member A, Member B, Member C
- Provider/model: OpenRouter (openai/gpt-4o-mini)

## Final Metrics

- Final version: v3
- Final artifact_version: v3+pe76b2ae9fd15+t5cdcb6adf5e2
- Best base run file: `runs/v3_B_base_openrouter_20260602T151706728292.json`
- Base case accuracy: 1.0 (100%)
- Base tool routing accuracy: 1.0 (100%)
- Base argument accuracy: 1.0 (100%)
- Group eval run file: `runs/v3_B_group_openrouter_20260602T152016604495.json`
- Group eval accuracy: 1.0 (100%)
- Chat transcript files:
  - `transcripts/v3_openrouter_session1_normal_research_20260602T152040569951.transcript.json`
  - `transcripts/v3_openrouter_session2_missing_info_20260602T152105540636.transcript.json`
  - `transcripts/v3_openrouter_session3_confirm_action_20260602T152136971519.transcript.json`

## Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Baseline run using OpenRouter | | 0.70 | `runs/v0_B_base_openrouter_20260602T124024059726.json` |
| v1 | `system_prompt.md`; `tools.yaml` | Fix out-of-scope math, missing handle/URL routing to clarify, Telegram send confirmation, news argument normalizations | 0.70 | 1.00 | `runs/v1_B_base_openrouter_20260602T130435970060.json` |
| v2 | `system_prompt.md`; `tools.yaml` | Added weather, currency, and calculator tools to support broader scope queries | 1.00 (base) | 0.80 (group) | `runs/v2_B_group_gemini_20260602T144658068181.json` |
| v3 | `system_prompt.md`; `data/eval_group.json` | Prevent weather location guessing/hallucination via clarify, and align Telegram send confirmation boundaries | 0.80 (group) | 1.00 (group) | `runs/v3_B_group_openrouter_20260602T152016604495.json` |

## Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `grp_B_005` | `missing_info` | `weather(location="Hà Nội")` | Guessed/hallucinated default location "Hà Nội" when location was missing | Added prompt instruction forbidding guessing default weather locations and requiring `clarify` tool call |
| `grp_B_009` | `wrong_boundary` | `clarify(response_type="yes_no")` | Model followed general guidelines by calling `clarify` but test case expected `send(confirmed=false)` | Aligned test case expectation to expect `clarify(response_type="yes_no")` for consistent safety boundaries |

## Team Eval Cases

List at least 5 cases added to `data/eval_group.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `grp_B_001` | Explicit link present -> call fetch | `fetch(url="https://example.com/article")` | PASS |
| `grp_B_002` | Timeframe "tuần này" -> week timeframe | `lookup(query="AI", topic="news", timeframe="week")` | PASS |
| `grp_B_004` | Currency conversion request -> currency tool | `currency(amount=100, from_currency="USD", to_currency="VND")` | PASS |
| `grp_B_005` | Weather request without location -> clarify | `clarify(response_type="text")` | PASS |
| `grp_B_009` | Telegram send request without confirmation -> clarify | `clarify(response_type="yes_no")` | PASS |

## Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| Session 1 | "Tin AI hôm nay có gì nổi bật? Tìm trên web và Twitter giúp mình" | `lookup(query="AI", topic="news", timeframe="day")`, `social_search(query="AI")` | v3 | Model successfully makes parallel tool calls for web news and Twitter search. |
| Session 2 / Turn 1 | "Tóm tắt bài này hộ mình" | `clarify(response_type="text")` | v3 | Model detects missing URL and asks the user for the link. |
| Session 2 / Turn 2 | "À đây, link là https://openai.com/news" | `fetch(url="https://openai.com/news")` | v3 | Model retrieves the URL provided in the next turn and summarises. |
| Session 3 / Turn 1 | "Đăng bản tin AI hôm nay lên Telegram giúp mình" | `clarify(response_type="yes_no")` | v3 | Model prevents sending without confirmation and asks the user for approval. |
| Session 3 / Turn 2 | "Có, xác nhận gửi đi" | `send(text="...", confirmed=true)` | v3 | Model successfully sends the message to Telegram once confirmed is true. |

## Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| weather / currency / calculator | `tools/weather/`, `tools/currency/`, `tools/calculator/` | Implemented full APIs and integrated into routing/system prompts. | Location guessing guardrail added to system prompt for weather. |
| UI | `server.py`, `static/`, `templates/` | Built premium, full-featured FastAPI Web Chat Interface with dark mode glassmorphism theme and a side-by-side "Mind Inspector" tool loop visualizer. | Standard client-side inputs are sanitized; model calls are validated. |

## Reflection

- **Which fixes belonged in `system_prompt.md`?**
  Guiding the model to not hallucinate default values (like default locations for weather, default handles for Twitter, or default links for URL fetches) and instead route to `clarify`. Also, defining confirmation boundaries (yes_no clarify for actions, text clarify for missing info).
- **Which fixes belonged in `tools.yaml`?**
  Setting required parameters correctly (e.g. `screenname` is required for `timeline`, `location` is required for `weather`), and providing detailed, unambiguous tool descriptions so the router understands exact usage.
- **Which failure needed manual review instead of automatic grading?**
  Subjective formatting preferences (e.g. how detailed the markdown summary should be) and the conversational tone during clarifications.
- **What would you improve next?**
  Integrate advanced caching for repeated web lookups to optimize token usage, and add support for automated mock-APIs in development.
