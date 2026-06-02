---
name: pdf_download
track: bonus
kind: live_api_plus_local_save
provider: arXiv API + Direct HTTP
requires_env: [ARXIV_USER_AGENT]
inputs: [url, filename, download_folder]
outputs: [file_path, file_size, status, arxiv_id, download_method, fallback_used]
side_effect: local_file_write
---
# pdf_download

Downloads PDF files from any URL with optimized support for arXiv papers. Features automatic arXiv ID detection, rate limiting, and fallback mechanisms. Can specify custom filename and download folder location.
