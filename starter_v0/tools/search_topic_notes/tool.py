from __future__ import annotations

from pathlib import Path
from typing import Any

from tools._shared import ROOT, err, terms


NOTES_DIR = ROOT / "topic_notes"


def _sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    title = "Overview"
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if lines:
                sections.append((title, lines))
            title = line[3:].strip()
            lines = []
        elif line.startswith("# "):
            title = line[2:].strip()
        else:
            lines.append(line)
    if lines:
        sections.append((title, lines))
    return [(section_title, "\n".join(section_lines).strip()) for section_title, section_lines in sections if "\n".join(section_lines).strip()]


def search_topic_notes(query: str = "", top_k: int = 3) -> dict[str, Any]:
    try:
        query_terms = terms(query)
        if not query_terms:
            return {"tool": "search_topic_notes", "query": query, "results": []}

        hits: list[dict[str, Any]] = []
        for path in sorted(NOTES_DIR.glob("*.md")):
            raw = path.read_text(encoding="utf-8")
            doc_terms = terms(path.stem)
            for section, body in _sections(raw):
                section_terms = terms(" ".join([section, body]))
                score = len(query_terms & section_terms) + 2 * len(query_terms & doc_terms)
                if score <= 0:
                    continue
                excerpt = " ".join(line.strip() for line in body.splitlines() if line.strip())
                hits.append({
                    "doc_id": path.stem,
                    "section": section,
                    "excerpt": excerpt[:1000],
                    "score": score,
                    "source": str(path.relative_to(ROOT)),
                })

        hits.sort(key=lambda item: item["score"], reverse=True)
        return {
            "tool": "search_topic_notes",
            "query": query,
            "results": hits[: max(1, int(top_k or 3))],
            "freshness": "static_demo_focus_notes",
        }
    except Exception as exc:
        return err("search_topic_notes", exc)
