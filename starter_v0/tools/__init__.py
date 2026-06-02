from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Public tool names and folder names are verb-first, single-action names.
# The imported function names are the underlying implementations.
from .ask_user.tool import ask_user
from .get_user_timeline.tool import get_user_tweets
from .read_paper_text.tool import get_arxiv_paper_text
from .read_url.tool import read_url
from .render_digest.tool import render_digest
from .search_papers.tool import arxiv_search
from .search_policy.tool import search_company_policy
from .search_social_posts.tool import search_tweets
from .search_topic_notes.tool import search_topic_notes
from .search_web.tool import web_search
from .send_message.tool import send_telegram


# NOTE: These keys are the names the model sees AND the names
# data/eval_base.json + data/eval_research_extension.json match against.
# If a team renames a tool, it MUST stay in sync across ALL of:
#   artifacts/tools.yaml  ->  this dict  ->  data/eval_base.json + data/eval_research_extension.json
# Otherwise the eval raises "not declared in tools.yaml" or scores every call as a name mismatch.
TOOL_FUNCTIONS = {
    "ask_user": ask_user,
    "get_user_timeline": get_user_tweets,
    "search_social_posts": search_tweets,
    "search_web": web_search,
    "read_url": read_url,
    "render_digest": render_digest,
    "send_message": send_telegram,
    "search_policy": search_company_policy,
    "search_topic_notes": search_topic_notes,
    "search_papers": arxiv_search,
    "read_paper_text": get_arxiv_paper_text,
}


def load_tool_declarations(path: Path) -> list[dict[str, Any]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "type": "function",
        "function": {
            "name": item["name"],
            "description": item.get("description", ""),
            "parameters": item.get("parameters", {"type": "object", "properties": {}}),
        },
    } for item in declarations]

