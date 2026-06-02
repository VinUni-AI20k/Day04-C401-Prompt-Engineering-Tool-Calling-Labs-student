---
name: paper_text
track: bonus
kind: live_api_plus_local_extract
provider: arXiv + pypdf
requires_env: [ARXIV_USER_AGENT]
inputs: [arxiv_url, max_pages, max_chars]
outputs: [items, pdf_path, txt_path, page_count]
side_effect: local_file_write
---
# paper_text

Download an arXiv paper PDF and extract its text content locally using `pypdf`. The extracted text is saved to disk and returned as an item. Use this after finding a paper with the `papers` tool to read its full content.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `arxiv_url` | string | **yes** | `""` | An arXiv URL or ID (e.g. `"https://arxiv.org/abs/2401.12345"` or `"2401.12345"`). |
| `max_pages` | integer | no | `5` | Maximum number of PDF pages to extract text from (1+). |
| `max_chars` | integer | no | `8000` | Maximum characters to return (1,000–20,000). |

## Return Format

```json
{
  "tool": "get_arxiv_paper_text",
  "arxiv_id": "2401.12345",
  "url": "https://arxiv.org/abs/2401.12345",
  "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf",
  "pdf_path": "starter_v0/arxiv_papers/2401.12345.pdf",
  "txt_path": "starter_v0/arxiv_papers/2401.12345.txt",
  "page_count": 12,
  "pages_read": 5,
  "chars_returned": 8000,
  "items": [
    {
      "title": "arXiv paper 2401.12345",
      "url": "https://arxiv.org/abs/2401.12345",
      "source": "arxiv.org",
      "summary": "Extracted text content..."
    }
  ]
}
```

## Notes

- **Side effect**: Downloads PDF and writes `.pdf` + `.txt` files to `starter_v0/arxiv_papers/`.
- Requires `pypdf` package (`pip install pypdf`).
- Requires `ARXIV_USER_AGENT` env var (defaults to a generic educational agent string).
- **Rate-limited**: waits at least 3 seconds between arXiv requests.
- The `summary` field in items contains the extracted text (truncated to `max_chars`).
- On error (invalid ID, network failure, missing pypdf), returns `{"tool": "get_arxiv_paper_text", "error": "..."}`.
