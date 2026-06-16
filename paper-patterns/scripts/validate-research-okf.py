#!/usr/bin/env python3
"""Validate a lightweight research-pattern OKF markdown bundle."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REQUIRED_FRONTMATTER = {"type", "title", "description", "tags", "timestamp"}
SKIP_NAMES = {"index.md", "log.md", "README.md"}


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, ["missing YAML frontmatter"]
    end = text.find("\n---", 4)
    if end == -1:
        return {}, ["unterminated YAML frontmatter"]
    raw = text[4:end].splitlines()
    fields: dict[str, str] = {}
    for line in raw:
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    missing = sorted(REQUIRED_FRONTMATTER - fields.keys())
    problems = [f"missing frontmatter field: {key}" for key in missing]
    return fields, problems


def iter_local_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    links: list[str] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if (
            not target
            or target.startswith("#")
            or "://" in target
            or target.startswith("mailto:")
        ):
            continue
        links.append(target.split("#", 1)[0])
    return links


def validate(root: Path) -> int:
    root = root.resolve()
    if not root.exists():
        print(f"error: bundle root does not exist: {root}", file=sys.stderr)
        return 2
    errors: list[str] = []
    warnings: list[str] = []

    for path in sorted(root.rglob("*.md")):
        if path.name in SKIP_NAMES:
            continue
        rel = path.relative_to(root)
        _, problems = parse_frontmatter(path)
        errors.extend(f"{rel}: {problem}" for problem in problems)

        for raw_link in iter_local_links(path):
            target = (path.parent / unquote(raw_link)).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                warnings.append(f"{rel}: link points outside bundle: {raw_link}")
                continue
            if not target.exists():
                errors.append(f"{rel}: broken local link: {raw_link}")

    if errors:
        print("errors:")
        for item in errors:
            print(f"- {item}")
    if warnings:
        print("warnings:")
        for item in warnings:
            print(f"- {item}")

    if errors:
        return 1
    print(f"ok: checked markdown concepts under {root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate research-pattern OKF markdown concept files"
    )
    parser.add_argument("root", help="Bundle root directory to validate")
    args = parser.parse_args()
    return validate(Path(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
