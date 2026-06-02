---
name: job_search
track: core
kind: live_api
provider: RapidAPI JSearch
requires_env: [RAPIDAPI_KEY, RAPIDAPI_JSEARCH_HOST]
inputs: [query, page, num_pages, limit]
outputs: [items]
side_effect: false
---

---
# job_search

Searches job postings by keyword. Returns job title, employer,
location, application link, posting date, and other job metadata.
