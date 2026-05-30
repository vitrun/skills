#!/usr/bin/env python3
"""Fetch recent AlphaXiv papers and format a paper digest.

This script is intentionally fetch/format only. Publishing and notifications are
handled by the paper-digest skill with lark-cli so private Lark targets never
live in this script.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


API_BASE = "https://api.alphaxiv.org"
TOPIC_KEYWORDS = (
    "agent",
    "alignment",
    "benchmark",
    "code",
    "computer-use",
    "diffusion",
    "evaluation",
    "inference",
    "language model",
    "llm",
    "multimodal",
    "reasoning",
    "reinforcement learning",
    "robot",
    "transformer",
    "vision-language",
    "world model",
)


def request_json(path: str, params: dict[str, str]) -> Any:
    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "paper-digest-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


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


def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def save_seen(path: Path, ids: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_seen(path)
    merged = sorted(existing | set(ids))
    path.write_text("\n".join(merged) + ("\n" if merged else ""), encoding="utf-8")


def text_for_filter(paper: dict[str, Any]) -> str:
    parts: list[str] = [str(paper.get("title") or ""), str(paper.get("abstract") or "")]
    summary = paper.get("paper_summary") or {}
    if isinstance(summary, dict):
        parts.append(str(summary.get("summary") or ""))
        for key in ("originalProblem", "solution", "results", "conclusion"):
            value = summary.get(key)
            if isinstance(value, list):
                parts.extend(str(item) for item in value)
            elif value:
                parts.append(str(value))
    return " ".join(parts).lower()


def keep_topic(paper: dict[str, Any]) -> bool:
    text = text_for_filter(paper)
    return any(keyword in text for keyword in TOPIC_KEYWORDS)


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


def extract_paper(paper: dict[str, Any]) -> dict[str, Any]:
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

    problems = as_list(summary.get("originalProblem")) or first_sentences(str(paper.get("abstract") or ""), 2)
    methods = as_list(summary.get("solution"))
    insights = as_list(summary.get("results")) or as_list(summary.get("conclusion")) or first_sentences(str(summary.get("summary") or ""), 2)

    return {
        "title": str(paper.get("title") or arxiv_id or "Untitled paper").strip(),
        "arxiv_id": arxiv_id,
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
        "alphaxiv_url": f"https://alphaxiv.org/overview/{versioned_id or arxiv_id}" if (versioned_id or arxiv_id) else "",
        "authors": authors[:8],
        "organizations": organizations[:4],
        "problem": [clamp(item) for item in problems[:2]],
        "method": [clamp(item) for item in methods[:2]],
        "insight": [clamp(item) for item in insights[:2]],
        "votes": (paper.get("metrics") or {}).get("total_votes"),
    }


def format_markdown(papers: list[dict[str, Any]], run_date: str) -> str:
    lines = [f"## {run_date} Paper Digest", ""]
    if not papers:
        lines.append("No new papers matched after deduplication and topic filtering.")
        return "\n".join(lines) + "\n"

    for paper in papers:
        lines.append(f"### {paper['title']}")
        if paper.get("arxiv_url"):
            lines.append(f"- arXiv: {paper['arxiv_url']}")
        if paper.get("alphaxiv_url"):
            lines.append(f"- AlphaXiv: {paper['alphaxiv_url']}")
        if paper.get("authors"):
            lines.append(f"- Authors: {', '.join(paper['authors'])}")
        if paper.get("organizations"):
            lines.append(f"- Institutions: {', '.join(paper['organizations'])}")
        for item in paper.get("problem") or []:
            lines.append(f"- **Problem:** {item}")
        for item in paper.get("method") or []:
            lines.append(f"- **Method:** {item}")
        for item in paper.get("insight") or []:
            lines.append(f"- **Insight/Result:** {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch AlphaXiv hot papers and format a digest")
    parser.add_argument("--limit", type=int, default=20, help="maximum papers to fetch")
    parser.add_argument("--interval", default="7 Days", help='AlphaXiv time window, e.g. "1 Day" or "7 Days"')
    parser.add_argument("--sort", default="Hot", help="AlphaXiv sort, e.g. Hot, New, Top")
    parser.add_argument("--output", choices=("md", "json"), default="md", help="output format")
    parser.add_argument("--cache-dir", default="~/.cache/paper-digest", help="dedupe cache directory")
    parser.add_argument("--no-cache", action="store_true", help="skip reading and writing dedupe cache")
    parser.add_argument("--no-cache-write", action="store_true", help="read dedupe cache but do not update it")
    parser.add_argument("--no-filter", action="store_true", help="skip topic filtering")
    parser.add_argument("--date", default=date.today().isoformat(), help="date for the digest heading")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = request_json(
        "/papers/v3/feed",
        {
            "pageNum": "1",
            "pageSize": str(args.limit),
            "sort": args.sort,
            "interval": args.interval,
        },
    )
    raw_papers = data if isinstance(data, list) else (data.get("papers") or data.get("data") or [])
    if not isinstance(raw_papers, list):
        raise RuntimeError("unexpected AlphaXiv feed response shape")

    cache_path = Path(os.path.expanduser(args.cache_dir)) / "seen_ids.txt"
    seen = set() if args.no_cache else load_seen(cache_path)
    new_raw = [p for p in raw_papers if normalize_arxiv_id(canonical_arxiv_id(p)) not in seen]
    filtered_raw = new_raw if args.no_filter else [p for p in new_raw if keep_topic(p)]
    papers = [extract_paper(p) for p in filtered_raw]

    ids = [paper["arxiv_id"] for paper in papers if paper.get("arxiv_id")]
    if not args.no_cache and not args.no_cache_write:
        save_seen(cache_path, ids)

    meta = {
        "fetched_count": len(raw_papers),
        "new_count": len(new_raw),
        "filtered_count": len(papers),
        "date": args.date,
        "papers": papers,
    }

    print(
        f"[INFO] fetched={len(raw_papers)} new={len(new_raw)} filtered={len(papers)}",
        file=sys.stderr,
    )
    if args.output == "json":
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(papers, args.date), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
