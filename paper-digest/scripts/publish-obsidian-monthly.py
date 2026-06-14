#!/usr/bin/env python3
"""Publish a paper digest into a monthly Obsidian note with prepend semantics."""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish paper-digest output to a monthly Obsidian note")
    parser.add_argument("--vault-path", required=True, help="absolute Obsidian vault path")
    parser.add_argument("--subdir", default="Papers/Digests", help="subdirectory inside the vault")
    parser.add_argument("--vault-name", default="", help="optional Obsidian vault name for obsidian:// URI")
    parser.add_argument("--digest-path", required=True, help="path to final curated digest markdown")
    parser.add_argument("--preview-path", default="", help="optional preview.json for verification")
    parser.add_argument("--run-date", default=datetime.now().strftime("%Y-%m-%d"), help="digest run date")
    parser.add_argument(
        "--run-stamp",
        default=datetime.now().strftime("%Y-%m-%dT%H%M%S"),
        help="unique batch stamp used in the inserted marker",
    )
    parser.add_argument("--file", default="", help="optional explicit note filename")
    parser.add_argument("--output-json", default="", help="optional path for publish result json")
    return parser.parse_args()


def load_preview_first_url(preview_path: str) -> str:
    if not preview_path:
        return ""
    preview = json.loads(Path(preview_path).read_text(encoding="utf-8"))
    papers = preview.get("papers") or []
    if not isinstance(papers, list) or not papers:
        return ""
    return str((papers[0] or {}).get("arxiv_url") or "")


def ensure_frontmatter(dest_path: Path, title: str) -> None:
    if dest_path.exists():
        return
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    created = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    dest_path.write_text(
        "\n".join(
            [
                "---",
                f'title: "{title}"',
                f'created: "{created}"',
                'source: "paper-digest"',
                "tags:",
                "  - paper-digest",
                "  - automation",
                "---",
                "",
            ]
        ),
        encoding="utf-8",
    )


def split_frontmatter(existing: str) -> tuple[str, str]:
    if not existing.startswith("---\n"):
        return "", existing
    end = existing.find("\n---\n", 4)
    if end == -1:
        return "", existing
    fm_end = end + len("\n---\n")
    return existing[:fm_end], existing[fm_end:]


def build_insert_block(marker: str, digest_body: str) -> str:
    return f"{marker}\n\n{digest_body.rstrip()}\n\n"


def destination_ref(vault_name: str, subdir: str, filename: str, dest_path: Path) -> str:
    if vault_name:
        rel_file = f"{subdir}/{filename}" if subdir else filename
        return f"obsidian://open?vault={vault_name}&file={urllib.parse.quote(rel_file)}"
    return str(dest_path)


def main() -> int:
    args = parse_args()
    vault_path = Path(os.path.expanduser(args.vault_path)).resolve()
    digest_path = Path(args.digest_path).resolve()
    digest_body = digest_path.read_text(encoding="utf-8").strip()

    month_stamp = args.run_date[:7]
    title = f"{month_stamp} Paper Digest"
    filename = args.file or f"{month_stamp} Paper Digest.md"
    subdir = args.subdir.strip().strip("/")
    dest_dir = vault_path / subdir if subdir else vault_path
    dest_path = dest_dir / filename
    marker = f"<!-- paper-digest:{args.run_stamp} -->"

    ensure_frontmatter(dest_path, title)
    existing = dest_path.read_text(encoding="utf-8")
    frontmatter, remainder = split_frontmatter(existing)
    new_body = build_insert_block(marker, digest_body) + remainder.lstrip("\n")
    dest_path.write_text(frontmatter + ("\n" if frontmatter and not frontmatter.endswith("\n\n") else "") + new_body, encoding="utf-8")

    written = dest_path.read_text(encoding="utf-8")
    first_url = load_preview_first_url(args.preview_path)
    h3_count = sum(1 for line in written.splitlines() if line.startswith("### "))
    ok = marker in written and h3_count >= 1 and (not first_url or first_url in written)
    verification = "marker+h3" if ok and not first_url else "marker+h3+url" if ok else "failed"

    result: dict[str, Any] = {
        "ok": ok,
        "destination_ref": destination_ref(args.vault_name, subdir, filename, dest_path),
        "verification": verification,
        "dest_path": str(dest_path),
        "marker": marker,
        "file": filename,
        "run_date": args.run_date,
        "month_stamp": month_stamp,
    }
    if first_url:
        result["verified_url"] = first_url

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
