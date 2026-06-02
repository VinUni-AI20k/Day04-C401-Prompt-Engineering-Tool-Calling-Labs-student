# GitHub Search Tool

Search GitHub repositories for open-source code, developer tools, libraries, or frameworks.

## Parameters

*   `query` (string, required): The search keyword or phrase (e.g., `"react library"`, `"transformers"`, `"machine learning codebase"`).
*   `limit` (integer, optional, default: 5): Max number of repositories to return.

## Returns

A JSON object containing:
*   `status`: `"success"` or `"error"`.
*   `query`: The original search term.
*   `results`: List of matching repositories with `name`, `description`, `url`, `stars`, `forks`, `language`, and `updated_at`.
