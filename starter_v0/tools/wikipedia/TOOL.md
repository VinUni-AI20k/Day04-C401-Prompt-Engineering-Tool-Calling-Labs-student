# Wikipedia Search Tool

Search Wikipedia for general information, history, concepts, summaries, or encyclopedia lookup.

## Parameters

*   `query` (string, required): The topic or keywords to search for. E.g., `"artificial intelligence"`, `"Quantum mechanics"`.
*   `limit` (integer, optional, default: 3): Number of matching articles to retrieve.

## Returns

A JSON object containing:
*   `status`: `"success"` or `"error"`.
*   `query`: The original search term.
*   `results`: List of matching articles with `title`, `url`, `summary`, and `description`.
