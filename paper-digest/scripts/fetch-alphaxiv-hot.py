#!/usr/bin/env python3
"""Fetch recent AlphaXiv papers and format a paper digest.

This script is intentionally fetch/format only. Publishing and notifications are
handled by the paper-digest skill's configured destination so private targets
never live in this script.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

from paper_digest_lib import extract_paper, canonical_arxiv_id, normalize_arxiv_id


API_BASE = "https://api.alphaxiv.org"


def request_json(path: str, params: dict[str, str]) -> Any:
    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "paper-digest-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def save_seen(path: Path, ids: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_seen(path)
    merged = sorted(existing | set(ids))
    path.write_text("\n".join(merged) + ("\n" if merged else ""), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch AlphaXiv hot papers and format a digest")
    parser.add_argument("--limit", type=int, default=20, help="maximum papers to fetch")
    parser.add_argument("--interval", default="7 Days", help='AlphaXiv time window, e.g. "1 Day" or "7 Days"')
    parser.add_argument("--sort", default="Hot", help="AlphaXiv sort, e.g. Hot, New, Top")
    parser.add_argument("--output", choices=("md", "json"), default="md", help="output format")
    parser.add_argument("--cache-dir", default="~/.cache/paper-digest", help="dedupe cache directory")
    parser.add_argument("--no-cache", action="store_true", help="skip reading and writing dedupe cache")
    parser.add_argument("--no-cache-write", action="store_true", help="read dedupe cache but do not update it")
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
    papers = [extract_paper(p, source_rank=index + 1) for index, p in enumerate(new_raw)]

    ids = [paper["arxiv_id"] for paper in papers if paper.get("arxiv_id")]
    if not args.no_cache and not args.no_cache_write:
        save_seen(cache_path, ids)

    meta = {
        "fetched_count": len(raw_papers),
        "new_count": len(new_raw),
        "candidate_count": len(papers),
        "date": args.date,
        "papers": papers,
    }

    print(
        f"[INFO] fetched={len(raw_papers)} new={len(new_raw)} candidates={len(papers)}",
        file=sys.stderr,
    )
    if args.output == "json":
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        from paper_digest_lib import format_markdown

        print(format_markdown(papers, args.date), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
