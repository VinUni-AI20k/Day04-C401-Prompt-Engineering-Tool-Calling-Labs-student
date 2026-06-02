---
name: fetch
track: core
kind: live_api
provider: Firecrawl
requires_env: [FIRECRAWL_API_KEY]
inputs: [url]
outputs: [items]
side_effect: false
---
# fetch

Scrape and read the content of a single URL using the Firecrawl API. Returns the page content as markdown. Use this when you need to read a specific webpage, article, or document.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | **yes** | `""` | The full URL to scrape (e.g. `"https://example.com/article"`). |

## Return Format

```json
{
  "tool": "read_url",
  "url": "https://example.com/article",
  "items": [
    {
      "title": "Page Title",
      "url": "https://example.com/article",
      "source": "example.com",
      "summary": "Markdown content of the page (truncated to 4000 chars)..."
    }
  ]
}
```

## Notes

- Requires `FIRECRAWL_API_KEY` environment variable.
- Content is returned as markdown, truncated to **4,000 characters**.
- The `source` field is the domain extracted from the URL.
- Timeout is 60 seconds (longer than other tools due to scraping).
- On error, returns `{"tool": "read_url", "error": "..."}`.
