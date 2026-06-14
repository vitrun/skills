#!/usr/bin/env python3
"""Materialize the agent-curated paper digest artifacts.

This helper converts a raw fetch preview plus an explicit agent-authored
selection file into the final preview JSON and publishable Markdown digest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from paper_digest_lib import format_markdown, normalize_arxiv_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize curated paper-digest artifacts")
    parser.add_argument("--raw-preview", required=True, help="path to raw candidate preview json")
    parser.add_argument("--selection-file", required=True, help="path to agent-authored selection json")
    parser.add_argument("--output-json", required=True, help="path to final curated preview json")
    parser.add_argument("--output-md", required=True, help="path to final digest markdown")
    parser.add_argument("--date", required=True, help="date for the digest heading")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_selection_id(entry: dict[str, Any]) -> str:
    for key in ("arxiv_id", "id", "paper_id"):
        value = str(entry.get(key) or "").strip()
        if value:
            return normalize_arxiv_id(value)
    raise ValueError(f"selection entry missing paper id: {entry}")


def main() -> int:
    args = parse_args()
    raw_preview = load_json(Path(args.raw_preview))
    selection = load_json(Path(args.selection_file))

    candidate_papers = raw_preview.get("papers") or []
    if not isinstance(candidate_papers, list):
        raise ValueError("raw preview papers must be a list")

    selection_entries = selection.get("selected_papers") or selection.get("papers") or []
    if not isinstance(selection_entries, list):
        raise ValueError("selection file selected_papers must be a list")

    by_id = {
        normalize_arxiv_id(str(paper.get("arxiv_id") or "")): paper
        for paper in candidate_papers
        if str(paper.get("arxiv_id") or "").strip()
    }

    curated_papers: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, entry in enumerate(selection_entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"selection entry must be an object: {entry}")
        paper_id = normalize_selection_id(entry)
        if paper_id in seen_ids:
            raise ValueError(f"duplicate selected paper id: {paper_id}")
        source_paper = by_id.get(paper_id)
        if source_paper is None:
            raise ValueError(f"selected paper id not found in raw preview: {paper_id}")

        curated_paper = dict(source_paper)
        curated_paper["curation_rank"] = index
        if "preference_score" in entry:
            curated_paper["preference_score"] = entry["preference_score"]
        if "why_selected" in entry:
            curated_paper["why_selected"] = entry["why_selected"]
        elif "reason" in entry:
            curated_paper["why_selected"] = entry["reason"]
        curated_papers.append(curated_paper)
        seen_ids.add(paper_id)

    output = {
        "date": args.date,
        "fetched_count": raw_preview.get("fetched_count"),
        "new_count": raw_preview.get("new_count"),
        "candidate_count": raw_preview.get("candidate_count", len(candidate_papers)),
        "filtered_count": len(curated_papers),
        "selected_count": len(curated_papers),
        "preferences_applied": selection.get("preferences_applied", True),
        "preference_summary": selection.get("preference_summary", ""),
        "papers": curated_papers,
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(format_markdown(curated_papers, args.date), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
