# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v6, failure, eval, chat) dựa trên log thật.

## Team

- Team: Zone 1 Nhom 2
- Members: VuQuangBao + teammates
- Provider/model: OpenRouter / openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent đa năng: tìm tin tức trên web, đọc tweet theo tài khoản hoặc chủ đề, đọc nội dung URL, tìm paper arXiv, tìm repo GitHub trending, tìm thảo luận Reddit, dịch văn bản, tóm tắt kết quả thành digest, và gửi bản tin lên Telegram sau khi xác nhận. Agent tự động hỏi lại khi thiếu thông tin và từ chối các yêu cầu ngoài phạm vi nghiên cứu.

**Link dùng thử (deploy):**

URL: https://know-austin-agency-breeding.trycloudflare.com

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (handle, URL, xác nhận) | không |
| timeline | Lấy tweet gần đây của một tài khoản (map tên → handle) | không |
| social_search | Tìm tweet theo chủ đề/từ khóa (Latest hoặc Top) | không |
| lookup | Tìm tin tức/thông tin trên web (topic: news/general, timeframe: day/week/month) | không |
| fetch | Đọc nội dung một URL cụ thể | không |
| format | Trình bày danh sách kết quả thành markdown digest | không |
| send | Gửi bản tin lên Telegram (bắt buộc xác nhận trước khi gửi) | không |
| policy | Tìm trong company policy nội bộ theo 5 nhóm chủ đề | không |
| papers | Tìm paper khoa học trên arXiv | không |
| paper_text | Tải PDF arXiv và trích xuất nội dung text | không |
| reddit_search | Tìm thảo luận cộng đồng trên Reddit theo từ khóa/subreddit | **có** |
| github_trending | Tìm repo GitHub phổ biến theo chủ đề và ngôn ngữ lập trình | **có** |
| translate | Dịch văn bản giữa các ngôn ngữ (vi, en, ja, zh, ko, fr, de…) | **có** |
| summarize | Tóm tắt danh sách kết quả thành bản tin ngắn gọn có đánh số | **có** |

## A3. Câu hỏi mẫu để thử

1. `Tweet mới nhất của Sam Altman là gì?`
2. `Tin tức AI hôm nay có gì nổi bật?`
3. `Tìm repo GitHub trending về AI agents viết bằng Python trong tuần này`
4. `Mọi người đang bàn gì về ChatGPT trên Reddit?`
5. `Tóm tắt bài này giúp mình: https://openai.com/research/`
6. `Đăng bản tin này lên Telegram giúp mình` *(agent sẽ hỏi xác nhận trước)*

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Final Metrics

| Metric | v0 (baseline) | v6 (final) |
|--------|:---:|:---:|
| Case Accuracy (base 20 cases) | 0.70 | **1.00** |
| Tool Routing Accuracy | 0.75 | **1.00** |
| Argument Accuracy | 0.70 | **1.00** |
| Multi-turn Accuracy | 1.00 | **1.00** |
| Group Eval Accuracy (11 cases) | — | **1.00** |
| Extension Eval Accuracy (10 cases) | — | **1.00** |

- Final version: v6
- Final artifact_version: `v6+pf49c4834d448+td97d527cc93d`
- Best base run file: `runs/v6_B_base_openrouter_20260602T144742183544.json`
- Group eval run file: `runs/v5_B_group_openrouter_20260602T144454365957.json`
- Extension eval run file: `runs/v4_B_extension_openrouter_20260602T143604789552.json`
- Chat transcript file: `transcripts/v6_openrouter_20260602T144759404926.transcript.json`

## B2. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (intentionally bad prompt) | N/A | N/A | 0.75 | v0_B_base_openrouter_20260602T124633190428.json |
| v1 | system_prompt.md | Xóa 3 rules sai (đừng hỏi lại / tự đoán / gửi ngay / chỉ 1 tool) + thêm routing, boundary, parallel rules → fix R10/R11/R12/R13 | 0.75 | 0.95 | v1_B_base_openrouter_20260602T124902719765.json |
| v2 | system_prompt.md | Thêm tool-switching rule: khi user nói "bỏ X, chuyển sang Y" → chỉ gọi Y, không gọi cả X → fix M06 | 0.95 | 1.00 | v2_B_base_openrouter_20260602T125158112768.json |
| v3 | system_prompt.md | Mở rộng out-of-scope examples (thời tiết/nấu ăn/thể thao) + thêm policy_area routing cho 5 nhóm → fix G05/E01/E08 | 1.00 | 1.00 | v3_B_base_openrouter_20260602T141705296291.json |
| v4 | system_prompt.md + tools.yaml | Thêm parallel research+policy rule; thêm 4 tools mới (reddit_search/translate/github_trending/summarize); build Streamlit UI → fix E06 regression | 1.00 | 1.00 | v4_B_base_openrouter_20260602T143448702683.json |
| v5 | system_prompt.md | Thêm routing rules cho 4 tools mới + 4 eval cases multi-turn (G08–G11) → agent routing đúng reddit/github/translate thay vì fallback về lookup/social_search | 1.00 | 1.00 | v5_B_group_openrouter_20260602T144454365957.json |
| v6 | (không đổi) | Final verification: re-run base eval 20 cases để xác nhận không regression sau khi thêm rules v5 | 1.00 | 1.00 | v6_B_base_openrouter_20260602T144742183544.json |

## B3. Failure Analysis (v0 baseline)

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix (v1) |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là x³/3+C")` | Câu hỏi toán học → agent gọi `send` thay vì từ chối | Thêm out-of-scope rule + ví dụ cụ thể |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Thiếu tên tài khoản → agent đoán bừa "sama" thay vì hỏi lại | Xóa rule "đừng hỏi lại", thêm clarify rule |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Thiếu URL → agent tự bịa URL thay vì hỏi lại | Xóa rule "tự đoán URL", thêm clarify rule |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin đã đăng...")` (không confirm) | Gửi Telegram ngay không hỏi xác nhận | Thêm boundary rule: gọi clarify yes_no trước send |
| R13_parallel_web_and_tweets | wrong_tool | `lookup(topic missing)` + `social_search(query="AI")` | Lookup thiếu `topic: news` | Thêm convention rule: topic=news khi user hỏi tin tức |
| R14_out_of_scope_coding | out_of_scope | gọi tool (v0) | Câu hỏi coding → agent gọi tool | Thêm coding vào danh sách out-of-scope |

## B4. Team Eval Cases

| Case ID | Type | What It Tests | Expected Tool | Result |
|---|---|---|---|---|
| G01_karpathy_handle_mapping | single | Map tên Andrej Karpathy → handle karpathy | `timeline(screenname="karpathy")` | PASS |
| G02_missing_topic_on_social_search | single | "phổ biến nhất" → search_type=Top | `social_search(search_type="Top")` | PASS |
| G03_missing_screenname_generic | single | "anh ấy" không xác định → hỏi lại | `clarify(response_type="text")` | PASS |
| G04_news_month_timeframe | single | "trong tháng này" → timeframe=month | `lookup(topic="news", timeframe="month")` | PASS |
| G05_weather_out_of_scope | single | Thời tiết → không gọi tool | no_tool (refuse) | PASS |
| G06_multiturn_switch_source_and_limit | multi | 3 turns: bỏ Twitter → web news Tesla tuần này | `lookup(query="Tesla", topic="news", timeframe="week")` | PASS |
| G07_parallel_two_persons_timeline | single | Tweet 2 người cùng lúc → 2 timeline song song | `timeline(sama)` + `timeline(elonmusk)` | PASS |
| G08_reddit_subreddit_refinement | multi | 3 turns: carry query + nhận subreddit + sort=hot | `reddit_search(query="AI agents", subreddit="LocalLLaMA", sort="hot")` | PASS |
| G09_github_trending_language_filter | multi | 3 turns: topic + language=python + since=weekly | `github_trending(topic="llm", language="python", since="weekly")` | PASS |
| G10_translate_language_correction | multi | 3 turns: user sửa target_lang vi→ja | `translate(text="...", target_lang="ja")` | PASS |
| G11_parallel_reddit_and_web | multi | 3 turns: 2 nguồn web + Reddit song song | `lookup(news, day)` + `reddit_search("Gemini 2.0")` | PASS |

## B5. Live Chat Evidence

Transcript: `transcripts/v6_openrouter_20260602T144759404926.transcript.json`

| Turn | User Request | Tool Calls | Outcome |
|---|---|---|---|
| 1 | Tìm repo GitHub trending về AI agents viết bằng Python trong tuần này | `github_trending(topic="ai-agents", language="python", since="weekly")` | Trả về 10 repos thật, có tên + stars + mô tả |
| 2 | Tìm thêm thảo luận về AI agents trên Reddit, trong subreddit MachineLearning | `reddit_search(query="AI agents", subreddit="MachineLearning", sort="relevance")` | Gọi đúng tool, đúng subreddit |
| 3 | Dịch câu này sang tiếng Nhật: "AI agents are the future of automation" | `translate(text="AI agents are the future of automation", target_lang="ja")` | Dịch đúng: "AIエージェントは自動化の未来です" |

Transcript bổ sung (v3): `transcripts/v3_openrouter_20260602T125711281080.transcript.json`

## B6. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts/v0_openrouter_20260602T141204028642.transcript.json` | Agent gọi `send(confirmed=True)` để gửi Telegram; v0 gửi ngay không hỏi (bug đã sửa ở v1) | Sau v1: bắt buộc gọi `clarify(yes_no)` trước, `send` chỉ chạy khi `confirmed=true` |
| arXiv/company policy | `runs/v4_B_extension_openrouter_20260602T143604789552.json` | 10/10 extension cases PASS; agent routing đúng `papers`, `paper_text`, `policy` với `policy_area` chính xác | policy_area luôn được set explicit, không để mặc định `all` |
| UI (Streamlit) | `app.py` | Streamlit chạy local port 8501; expose public qua Cloudflare Tunnel | Link tunnel tạm thời, sống theo phiên cloudflared |
| 4 tools mới | `tools/reddit_search/`, `tools/github_trending/`, `tools/translate/`, `tools/summarize/` | Đủ TOOL.md + tool.py + đăng ký __init__.py + tools.yaml | reddit_search phụ thuộc Reddit public API (không cần key); translate dùng MyMemory free tier (max 500 chars/request) |

## B7. Reflection

**Fixes thuộc `system_prompt.md`:**
- Rules hành vi: khi nào hỏi lại, khi nào từ chối, khi nào gửi xác nhận, khi nào gọi parallel
- Tool routing logic: map tên người → Twitter handle, từ khóa timeframe/search_type, routing reddit vs web vs social
- Out-of-scope examples cụ thể (thời tiết, nấu ăn, toán, coding)

**Fixes thuộc `tools.yaml`:**
- Thêm description rõ ràng để model phân biệt `reddit_search` vs `social_search`, `github_trending` vs `lookup`
- Khai báo enum values cho `sort`, `since`, `policy_area` để model chọn đúng giá trị

**Failure cần manual review:**
- R13 (v0): eval báo PASS nhưng thực ra `topic` arg bị thiếu — automated grading chỉ check tên tool, không check đủ tất cả required args. Cần human review với subset_matching chặt hơn.
- R08 (v0): agent gọi `send` để trả lời câu toán học — behavior kỳ lạ, cần đọc actual transcript để hiểu tại sao model chọn send thay vì lookup hay text answer.

**Cải thiện tiếp theo:**
- Thêm eval cases cho edge case: query có cả tên người lẫn chủ đề (vd: "tweet của Elon về Tesla")
- Strict arg checking trong eval: verify tất cả args, không chỉ tool name
- Thêm `summarize` vào eval cases — chưa có case nào test tool này
- Rate limit handling cho reddit_search (hiện không có retry khi bị 429)
