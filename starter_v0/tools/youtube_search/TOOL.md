# YouTube Search Tool

Search for YouTube videos, explainers, tutorials, or documentaries related to a research topic.

## Parameters

*   `query` (string, required): Keywords to search for on YouTube (e.g., `"deep learning basics"`, `"spacex launch 2026"`).
*   `limit` (integer, optional, default: 5): Maximum number of video results to return.

## Returns

A JSON object containing:
*   `status`: `"success"` or `"error"`.
*   `query`: The original search term.
*   `results`: List of matching videos with `title`, `url` (link), `description`, and relevance `score`.
