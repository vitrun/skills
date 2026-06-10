#!/usr/bin/env python3
"""Lightweight structural lint for this skills repository."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")
SECRET_RE = re.compile(
    r"(app_secret|access_token|refresh_token|secret_key|api[_-]?key|chat_id\s*=\s*oc_|doc_token\s*=|doxcn[A-Za-z0-9]{8,})",
    re.IGNORECASE,
)
ROUTING_TRIGGER_RE = re.compile(
    r"\b(use when|load when|when user|when the user|use for|use before|must use|for .+ when)\b",
    re.IGNORECASE,
)


@dataclass
class Finding:
    severity: str
    path: Path
    message: str


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        field = FIELD_RE.match(line)
        if field:
            key, value = field.groups()
            data[key] = value.strip().strip('"').strip("'")
    return data


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def relative(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def lint_skill(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    rel = relative(path, root)
    text = path.read_text(encoding="utf-8")
    meta = parse_frontmatter(text)
    body = FRONTMATTER_RE.sub("", text, count=1)
    words = word_count(body)
    lines = len(body.splitlines())

    if not meta.get("name"):
        findings.append(Finding("error", rel, "missing frontmatter name"))
    if not meta.get("description"):
        findings.append(Finding("error", rel, "missing frontmatter description"))
    else:
        desc = meta["description"]
        desc_words = word_count(desc)
        if desc_words > 60:
            findings.append(Finding("warn", rel, f"description is {desc_words} words; target 50-60 or fewer"))
        if not ROUTING_TRIGGER_RE.search(desc):
            findings.append(Finding("warn", rel, "description lacks an explicit routing trigger such as 'Use when'"))
        if re.search(r"\bhelps?\b", desc, re.IGNORECASE) and not re.search(r"\bwhen\b", desc, re.IGNORECASE):
            findings.append(Finding("warn", rel, "description reads like a capability summary instead of a routing rule"))

    if lines > 150:
        findings.append(Finding("warn", rel, f"SKILL.md body is {lines} lines; consider references/ or assets/"))
    if words > 1500:
        findings.append(Finding("warn", rel, f"SKILL.md body is {words} words; consider progressive disclosure"))

    skill_dir = path.parent
    has_resources = any((skill_dir / name).exists() for name in ("references", "scripts", "bin", "assets", "examples"))
    mentions_resources = re.search(r"\b(references/|scripts/|bin/|assets/|examples/)\b", text)
    if has_resources and not mentions_resources:
        findings.append(Finding("warn", rel, "skill has resource directories but SKILL.md does not point to them"))

    if SECRET_RE.search(text):
        findings.append(Finding("warn", rel, "possible secret or private ID pattern in SKILL.md"))

    return findings


def read_readme_skills(root: Path) -> set[str]:
    readme = root / "README.md"
    if not readme.exists():
        return set()
    text = readme.read_text(encoding="utf-8")
    return set(re.findall(r"^- \*\*([^*]+)\*\*", text, re.MULTILINE))


def parse_routing_eval_skills(path: Path) -> list[tuple[int, str]]:
    """Parse the simple routing eval seed format without requiring PyYAML."""
    refs: list[tuple[int, str]] = []
    active_list = False
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if stripped.startswith("- query:"):
            active_list = False
            continue
        if stripped in {"should_load:", "should_not_load:"}:
            active_list = True
            continue
        if stripped.endswith(":") and not stripped.startswith("- "):
            active_list = False
            continue
        if active_list and stripped.startswith("- "):
            refs.append((line_no, stripped[2:].strip().strip('"').strip("'")))
    return refs


def lint_routing_evals(root: Path, known_skills: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    path = root / "evals" / "skill-routing.yaml"
    rel = Path("evals/skill-routing.yaml")
    if not path.exists():
        return [Finding("warn", rel, "missing routing eval seed file")]

    text = path.read_text(encoding="utf-8")
    if "query:" not in text or "should_load:" not in text:
        findings.append(Finding("warn", rel, "routing eval file has no query/should_load entries"))
    if text.count("query:") < 5:
        findings.append(Finding("warn", rel, "routing eval file has fewer than 5 query examples"))

    for line_no, skill in parse_routing_eval_skills(path):
        if skill not in known_skills:
            findings.append(Finding("warn", rel, f"line {line_no} references unknown skill '{skill}'"))

    return findings


def lint_repo(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_files = sorted(
        path for path in root.glob("*/SKILL.md") if ".git" not in path.parts
    )
    readme_skills = read_readme_skills(root)
    known_skills = {path.parent.name for path in skill_files}
    for path in skill_files:
        meta_name = parse_frontmatter(path.read_text(encoding="utf-8")).get("name")
        if meta_name:
            known_skills.add(meta_name)

    for path in skill_files:
        findings.extend(lint_skill(path, root))
        skill_name = path.parent.name
        meta_name = parse_frontmatter(path.read_text(encoding="utf-8")).get("name")
        if skill_name not in readme_skills and (meta_name or skill_name) not in readme_skills:
            findings.append(Finding("warn", relative(path, root), "skill is not listed in README.md"))

    findings.extend(lint_routing_evals(root, known_skills))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a skills repository for routing and structure issues.")
    parser.add_argument("--root", default=".", help="Repository root to lint")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as errors")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = lint_repo(root)

    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warn"]

    for finding in findings:
        print(f"{finding.severity}: {finding.path}: {finding.message}")

    print(f"\nsummary: {len(errors)} errors, {len(warnings)} warnings")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
