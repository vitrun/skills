#!/usr/bin/env python3
"""Shared helpers for prompt-badcase-advisor scripts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

CONFIDENCE_VALUES = {"low", "medium", "high"}

JSON = dict[str, Any]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read_jsonl(path: Path) -> list[JSON]:
    rows: list[JSON] = []
    for line_no, line in enumerate(read_text(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: JSONL row must be an object")
        rows.append(value)
    return rows


def write_jsonl(path: Path, rows: list[JSON]) -> None:
    write_text(path, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def stable_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_path(path: Path, base: Path | None = None) -> str:
    base = base or Path.cwd()
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path.resolve())


def ensure_confidence(value: Any, path: str, errors: list[str]) -> None:
    if value not in CONFIDENCE_VALUES:
        errors.append(f"{path}: confidence must be one of {sorted(CONFIDENCE_VALUES)}")


def require_keys(obj: Any, keys: list[str], path: str, errors: list[str]) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{path}: must be an object")
        return
    for key in keys:
        if key not in obj:
            errors.append(f"{path}: missing required key {key!r}")


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip()).strip("_")
    return slug or fallback


def short_summary(text: str, limit: int = 180) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def discover_prompt_sections(text: str) -> list[JSON]:
    lines = text.splitlines()
    starts = _heading_starts(lines) + _xml_starts(lines)
    starts = _dedupe_starts(starts)
    candidates = _sections_from_starts(lines, starts) if starts else []
    if not candidates:
        candidates = _paragraph_sections(lines)
    return candidates


def _heading_starts(lines: list[str]) -> list[tuple[int, str, str, str]]:
    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    bold_re = re.compile(r"^\s*\*\*(?P<name>[A-Za-z0-9_][A-Za-z0-9_ -]{1,80})\*\*:?\s*$")
    starts: list[tuple[int, str, str, str]] = []
    for index, line in enumerate(lines):
        heading = heading_re.match(line)
        if heading:
            starts.append((index, heading.group(2).strip(), "markdown_heading", "high"))
            continue
        bold = bold_re.match(line)
        if bold:
            starts.append((index, bold.group("name").strip(), "bold_section", "high"))
    return starts


def _xml_starts(lines: list[str]) -> list[tuple[int, str, str, str]]:
    open_re = re.compile(r"^\s*<(?P<name>[A-Za-z0-9_][A-Za-z0-9_-]{1,80})>\s*$")
    starts: list[tuple[int, str, str, str]] = []
    used_ends: set[int] = set()
    for index, line in enumerate(lines):
        opened = open_re.match(line)
        if not opened:
            continue
        name = opened.group("name")
        close_re = re.compile(rf"^\s*</{re.escape(name)}>\s*$")
        for end in range(index + 1, len(lines)):
            if end in used_ends:
                continue
            if close_re.match(lines[end]):
                used_ends.add(end)
                starts.append((index, name, "xml_tag", "high"))
                break
    return starts


def _dedupe_starts(starts: list[tuple[int, str, str, str]]) -> list[tuple[int, str, str, str]]:
    by_line: dict[int, tuple[int, str, str, str]] = {}
    for item in starts:
        if item[0] not in by_line:
            by_line[item[0]] = item
    return sorted(by_line.values(), key=lambda item: item[0])


def _paragraph_sections(lines: list[str]) -> list[JSON]:
    sections: list[JSON] = []
    start = 0
    while start < len(lines):
        while start < len(lines) and not lines[start].strip():
            start += 1
        if start >= len(lines):
            break
        end = min(len(lines), start + 40)
        blank = next((i for i in range(start + 1, end) if not lines[i].strip()), end)
        end = blank if blank > start else end
        sections.append(_section_dict(lines, start, end, f"section_{len(sections) + 1:03d}", "paragraph_chunk", "low"))
        start = end + 1
    if not sections and not lines:
        sections.append(_section_dict([""], 0, 1, "section_001", "empty_prompt", "low"))
    return sections


def _sections_from_starts(lines: list[str], starts: list[tuple[int, str, str, str]]) -> list[JSON]:
    sections: list[JSON] = []
    starts = sorted(starts, key=lambda item: item[0])
    for idx, (start, name, method, confidence) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        sections.append(_section_dict(lines, start, end, name, method, confidence))
    return sections


def _section_dict(
    lines: list[str],
    start: int,
    end: int,
    name: str,
    method: str,
    confidence: str,
) -> JSON:
    text = "\n".join(lines[start:end]).strip()
    section_id = slugify(name, f"section_{start + 1}").lower()
    return {
        "section_id": section_id,
        "name": name,
        "line_start": start + 1,
        "line_end": max(start + 1, end),
        "summary": short_summary(text),
        "text_hash": stable_sha256(text),
        "detection_method": method,
        "confidence": confidence,
    }


def section_lookup(prompt_schema: JSON) -> set[str]:
    values: set[str] = set()
    for section in as_list(prompt_schema.get("sections")):
        if isinstance(section, dict):
            if section.get("section_id"):
                values.add(str(section["section_id"]))
            if section.get("name"):
                values.add(str(section["name"]))
    return values


def format_count_pairs(items: list[JSON], key: str, count_key: str = "count") -> str:
    if not items:
        return "none"
    return ", ".join(f"{item.get(key, 'unknown')}={item.get(count_key, 0)}" for item in items)
