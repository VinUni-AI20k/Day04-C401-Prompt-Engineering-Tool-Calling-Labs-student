from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from .search_images.tool import search_images
from .get_user_profile.tool import get_user_profile
from .ask_user.tool import ask_user
from .arxiv_search.tool import arxiv_search
from .get_arxiv_paper_text.tool import get_arxiv_paper_text
from .get_user_tweets.tool import get_user_tweets
from .read_url.tool import read_url
from .render_digest.tool import render_digest
from .search_company_policy.tool import search_company_policy
from .search_tweets.tool import search_tweets
from .send_telegram.tool import send_telegram
from .web_search.tool import web_search


TOOL_FUNCTIONS = {
    "ask_user": ask_user,
    "get_user_tweets": get_user_tweets,
    "search_tweets": search_tweets,
    "web_search": web_search,
    "read_url": read_url,
    "render_digest": render_digest,
    "send_telegram": send_telegram,
    "search_company_policy": search_company_policy,
    "arxiv_search": arxiv_search,
    "get_arxiv_paper_text": get_arxiv_paper_text,
    # Đăng ký mới cho v1 MVP
    "search_images": search_images,
    "get_user_profile": get_user_profile,

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

