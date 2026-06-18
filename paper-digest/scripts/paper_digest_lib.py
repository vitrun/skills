from __future__ import annotations

import re
import textwrap
from typing import Any


def normalize_arxiv_id(value: str) -> str:
    value = (value or "").strip()
    value = value.rsplit("/", 1)[-1]
    return re.sub(r"v\d+$", "", value)


def canonical_arxiv_id(paper: dict[str, Any]) -> str:
    for key in ("canonical_id", "universal_paper_id", "id"):
        value = str(paper.get(key) or "")
        if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", value):
            return value
    return str(paper.get("canonical_id") or paper.get("universal_paper_id") or "")


def as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def first_sentences(text: str, limit: int = 2) -> list[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    pieces = re.split(r"(?<=[.!?])\s+", text)
    return [piece.strip() for piece in pieces[:limit] if piece.strip()]


def clamp(text: str, width: int = 220) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= width:
        return text
    return textwrap.shorten(text, width=width, placeholder="...")


def paper_text_for_preference(paper: dict[str, Any]) -> str:
    parts: list[str] = [
        str(paper.get("title") or ""),
        str(paper.get("abstract") or ""),
        str(paper.get("summary") or ""),
    ]
    parts.extend(str(item) for item in paper.get("problem") or [])
    parts.extend(str(item) for item in paper.get("method") or [])
    parts.extend(str(item) for item in paper.get("insight") or [])
    return "\n".join(part for part in parts if part).strip()


def extract_paper(paper: dict[str, Any], source_rank: int) -> dict[str, Any]:
    versioned_id = canonical_arxiv_id(paper)
    arxiv_id = normalize_arxiv_id(versioned_id)
    summary = paper.get("paper_summary") or {}
    if not isinstance(summary, dict):
        summary = {}

    authors = as_list(paper.get("authors"))
    if not authors:
        authors = [item.get("full_name", "") for item in paper.get("full_authors", []) if isinstance(item, dict)]

    organizations = []
    for item in paper.get("organization_info") or []:
        if isinstance(item, dict):
            name = item.get("name") or item.get("display_name")
            if name:
                organizations.append(str(name))

    abstract = str(paper.get("abstract") or "").strip()
    summary_text = str(summary.get("summary") or "").strip()
    problems = as_list(summary.get("originalProblem")) or first_sentences(abstract, 2)
    methods = as_list(summary.get("solution"))
    insights = as_list(summary.get("results")) or as_list(summary.get("conclusion")) or first_sentences(summary_text, 2)

    return {
        "title": str(paper.get("title") or arxiv_id or "Untitled paper").strip(),
        "arxiv_id": arxiv_id,
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
        "alphaxiv_url": f"https://alphaxiv.org/overview/{versioned_id or arxiv_id}" if (versioned_id or arxiv_id) else "",
        "authors": authors[:8],
        "organizations": organizations[:4],
        "abstract": clamp(abstract, width=1200),
        "summary": clamp(summary_text, width=1200),
        "problem": [clamp(item) for item in problems[:2]],
        "method": [clamp(item) for item in methods[:2]],
        "insight": [clamp(item) for item in insights[:2]],
        "votes": (paper.get("metrics") or {}).get("total_votes"),
        "source_rank": source_rank,
        "preference_text": paper_text_for_preference(
            {
                "title": paper.get("title"),
                "abstract": abstract,
                "summary": summary_text,
                "problem": problems,
                "method": methods,
                "insight": insights,
            }
        ),
    }


def format_markdown(papers: list[dict[str, Any]], run_date: str) -> str:
    def append_group(label: str, items: list[str]) -> None:
        cleaned = [item for item in items if str(item).strip()]
        if not cleaned:
            return
        lines.append(f"- {label}:")
        for item in cleaned:
            lines.append(f"  - {item}")

    lines = [f"## {run_date} Paper Digest", ""]
    if not papers:
        lines.append("No new papers matched after deduplication and preference curation.")
        return "\n".join(lines) + "\n"

    for paper in papers:
        lines.append(f"### {paper['title']}")
        preferred_link = paper.get("arxiv_url") or paper.get("alphaxiv_url")
        if preferred_link:
            lines.append(f"- Link: {preferred_link}")
        if paper.get("authors"):
            lines.append(f"- Authors: {', '.join(paper['authors'])}")
        if paper.get("organizations"):
            lines.append(f"- Institutions: {', '.join(paper['organizations'])}")
        append_group("Problem", paper.get("problem") or [])
        append_group("Method", paper.get("method") or [])
        append_group("Insight/Result", paper.get("insight") or [])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
