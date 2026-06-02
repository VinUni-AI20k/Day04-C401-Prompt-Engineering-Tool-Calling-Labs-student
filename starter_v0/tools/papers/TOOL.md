---
name: papers
track: bonus
kind: live_api
provider: arXiv API
requires_env: [ARXIV_USER_AGENT]
inputs: [query, max_results, sort_by]
outputs: [items, total_results]
side_effect: false
---
# papers

Search academic papers on arXiv via the official Atom API. Use this for finding research papers, preprints, and scientific literature.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | **yes** | `""` | Search query. Plain keywords are auto-wrapped as `all:term`. You can also use arXiv field prefixes like `ti:`, `au:`, `cat:` directly. |
| `max_results` | integer | no | `5` | Number of results to return (1–10). |
| `sort_by` | string | no | `"relevance"` | Sort order: `"relevance"`, `"lastUpdatedDate"`, or `"submittedDate"`. |

## Return Format

```json
{
  "tool": "arxiv_search",
  "query": "transformer attention",
  "api_query": "all:transformer AND all:attention",
  "total_results": 1234,
  "items": [
    {
      "arxiv_id": "2401.12345",
      "title": "Paper Title",
      "summary": "Abstract text...",
      "authors": ["Author One", "Author Two"],
      "published": "2024-01-15T00:00:00Z",
      "updated": "2024-01-20T00:00:00Z",
      "url": "http://arxiv.org/abs/2401.12345",
      "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf",
      "source": "arxiv.org",
      "primary_category": "cs.CL",
      "categories": ["cs.CL", "cs.AI"]
    }
  ],
  "rate_limit_note": "arXiv may return 429 if called too frequently..."
}
```

## Notes

- Requires `ARXIV_USER_AGENT` env var (defaults to a generic educational agent string).
- **Rate-limited**: waits at least 3 seconds between requests; retries up to 3 times on 429.
- Keywords are joined with `AND` and prefixed with `all:` unless you use explicit field prefixes.
- Results are sorted in descending order.
- On error, returns `{"tool": "arxiv_search", "error": "..."}`.
