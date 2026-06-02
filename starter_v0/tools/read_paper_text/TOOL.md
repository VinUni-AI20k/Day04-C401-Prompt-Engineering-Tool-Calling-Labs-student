---
name: read_paper_text
track: bonus
kind: live_api_plus_local_extract
provider: arXiv + pypdf
requires_env: [ARXIV_USER_AGENT]
inputs: [arxiv_url, max_pages, max_chars]
outputs: [items, pdf_path, txt_path, page_count]
side_effect: local_file_write
---
# read_paper_text

Downloads an arXiv PDF and extracts text locally with `pypdf`. Output is saved
under `starter_v0/arxiv_papers/`.
