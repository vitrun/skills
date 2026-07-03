#!/usr/bin/env python3
"""Validate Prompt Advisor outputs and render reports."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from prompt_badcase_lib import (
    JSON,
    as_list,
    ensure_confidence,
    format_count_pairs,
    read_json,
    read_jsonl,
    require_keys,
    section_lookup,
    write_text,
)

BADCASE_REQUIRED = [
    "task_understanding.json",
    "badcase_schema.json",
    "failure_taxonomy.json",
    "badcase_evidence.jsonl",
    "badcase_attributions.jsonl",
    "badcase_report.md",
]
PROMPT_REQUIRED = [
    "prompt_schema.json",
    "prompt_section_attributions.jsonl",
    "advice.json",
]
FORBIDDEN_ADVICE_KEYS = {
    "patch",
    "diff",
    "final_prompt",
    "candidate_prompt",
    "rewritten_prompt",
    "direct_patch",
    "prompt_patch",
}


class ValidationError(RuntimeError):
    pass


def validate_run(run_dir: Path) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    badcase_dir = run_dir / "badcase_analysis"
    advice_dir = run_dir / "prompt_advice"

    for name in BADCASE_REQUIRED:
        if not (badcase_dir / name).exists():
            errors.append(f"missing badcase output: badcase_analysis/{name}")
    for name in PROMPT_REQUIRED:
        if not (advice_dir / name).exists():
            errors.append(f"missing prompt output: prompt_advice/{name}")
    if errors:
        raise ValidationError("\n".join(errors))

    validate_task_understanding(read_json(badcase_dir / "task_understanding.json"), errors)
    validate_badcase_schema(read_json(badcase_dir / "badcase_schema.json"), errors)
    validate_failure_taxonomy(read_json(badcase_dir / "failure_taxonomy.json"), errors)

    evidence = read_jsonl(badcase_dir / "badcase_evidence.jsonl")
    evidence_ids = validate_evidence(evidence, errors)
    validate_badcase_attributions(read_jsonl(badcase_dir / "badcase_attributions.jsonl"), evidence_ids, errors)

    prompt_schema = read_json(advice_dir / "prompt_schema.json")
    sections = validate_prompt_schema(prompt_schema, errors)
    validate_section_attributions(
        read_jsonl(advice_dir / "prompt_section_attributions.jsonl"),
        evidence_ids,
        sections,
        errors,
    )
    validate_advice(read_json(advice_dir / "advice.json"), evidence_ids, sections, errors)

    if errors:
        raise ValidationError("\n".join(errors))
    return warnings


def validate_task_understanding(data: JSON, errors: list[str]) -> None:
    require_keys(
        data,
        ["task_summary", "target_output", "quality_goals", "hard_constraints", "confidence", "uncertainties"],
        "task_understanding.json",
        errors,
    )
    ensure_confidence(data.get("confidence"), "task_understanding.json", errors)
    if not isinstance(data.get("uncertainties"), list):
        errors.append("task_understanding.json: uncertainties must be a list")


def validate_badcase_schema(data: JSON, errors: list[str]) -> None:
    require_keys(
        data,
        ["record_format", "conversation_fields", "human_labels", "score_fields", "metadata_fields", "confidence", "warnings"],
        "badcase_schema.json",
        errors,
    )
    ensure_confidence(data.get("confidence"), "badcase_schema.json", errors)


def validate_failure_taxonomy(data: JSON, errors: list[str]) -> None:
    require_keys(data, ["heads", "uncertainties"], "failure_taxonomy.json", errors)
    for idx, head in enumerate(as_list(data.get("heads"))):
        require_keys(head, ["id", "label", "severity", "definition", "source"], f"failure_taxonomy.heads[{idx}]", errors)


def validate_evidence(rows: list[JSON], errors: list[str]) -> set[str]:
    evidence_ids: set[str] = set()
    for idx, row in enumerate(rows):
        path = f"badcase_evidence.jsonl[{idx}]"
        require_keys(row, ["evidence_id", "case_id", "head", "severity", "quote", "why", "confidence"], path, errors)
        ensure_confidence(row.get("confidence"), path, errors)
        evidence_id = str(row.get("evidence_id", ""))
        if evidence_id in evidence_ids:
            errors.append(f"{path}: duplicate evidence_id {evidence_id}")
        evidence_ids.add(evidence_id)
    if not rows:
        errors.append("badcase_evidence.jsonl: must contain at least one evidence row")
    return evidence_ids


def validate_badcase_attributions(rows: list[JSON], evidence_ids: set[str], errors: list[str]) -> None:
    for idx, row in enumerate(rows):
        path = f"badcase_attributions.jsonl[{idx}]"
        require_keys(row, ["case_id", "heads", "uncertainties"], path, errors)
        if not isinstance(row.get("uncertainties"), list):
            errors.append(f"{path}: uncertainties must be a list")
        for head_idx, head in enumerate(as_list(row.get("heads"))):
            head_path = f"{path}.heads[{head_idx}]"
            require_keys(head, ["head", "severity", "confidence", "reason", "evidence_ids"], head_path, errors)
            ensure_confidence(head.get("confidence"), head_path, errors)
            check_evidence_refs(as_list(head.get("evidence_ids")), evidence_ids, head_path, errors)


def validate_prompt_schema(data: JSON, errors: list[str]) -> set[str]:
    require_keys(data, ["sections", "uncertainties"], "prompt_schema.json", errors)
    for idx, section in enumerate(as_list(data.get("sections"))):
        path = f"prompt_schema.sections[{idx}]"
        require_keys(
            section,
            ["section_id", "name", "line_start", "line_end", "summary", "text_hash", "detection_method", "confidence"],
            path,
            errors,
        )
        ensure_confidence(section.get("confidence"), path, errors)
    sections = section_lookup(data)
    if not sections:
        errors.append("prompt_schema.json: must define at least one section")
    return sections


def validate_section_attributions(
    rows: list[JSON],
    evidence_ids: set[str],
    sections: set[str],
    errors: list[str],
) -> None:
    for idx, row in enumerate(rows):
        path = f"prompt_section_attributions.jsonl[{idx}]"
        require_keys(row, ["case_id", "head", "evidence_ids", "suspected_sections"], path, errors)
        check_evidence_refs(as_list(row.get("evidence_ids")), evidence_ids, path, errors)
        for section_idx, item in enumerate(as_list(row.get("suspected_sections"))):
            item_path = f"{path}.suspected_sections[{section_idx}]"
            require_keys(item, ["section", "confidence", "reason"], item_path, errors)
            ensure_confidence(item.get("confidence"), item_path, errors)
            if str(item.get("section")) not in sections:
                errors.append(f"{item_path}: unknown prompt section {item.get('section')!r}")


def validate_advice(data: JSON, evidence_ids: set[str], sections: set[str], errors: list[str]) -> None:
    require_keys(data, ["schema", "run_id", "summary", "advice_cards"], "advice.json", errors)
    if data.get("schema") != "prompt_badcase_advice_v1":
        errors.append("advice.json: schema must be prompt_badcase_advice_v1")
    for idx, card in enumerate(as_list(data.get("advice_cards"))):
        path = f"advice.json.advice_cards[{idx}]"
        require_keys(
            card,
            [
                "advice_id",
                "head",
                "priority",
                "suspected_sections",
                "evidence_ids",
                "diagnosis",
                "suggestion",
                "risk",
                "human_questions",
                "confidence",
                "uncertainties",
                "not_a_patch",
            ],
            path,
            errors,
        )
        ensure_confidence(card.get("confidence"), path, errors)
        if card.get("not_a_patch") is not True:
            errors.append(f"{path}: not_a_patch must be true")
        if not isinstance(card.get("uncertainties"), list):
            errors.append(f"{path}: uncertainties must be a list")
        check_evidence_refs(as_list(card.get("evidence_ids")), evidence_ids, path, errors)
        for section in as_list(card.get("suspected_sections")):
            if str(section) not in sections:
                errors.append(f"{path}: unknown prompt section {section!r}")
        forbidden = FORBIDDEN_ADVICE_KEYS.intersection(card)
        if forbidden:
            errors.append(f"{path}: forbidden direct-patch keys present: {sorted(forbidden)}")
        suggestion = str(card.get("suggestion", "")).lower()
        if "```diff" in suggestion or "final prompt" in suggestion:
            errors.append(f"{path}: suggestion looks like a direct prompt patch or final prompt")
    if not as_list(data.get("advice_cards")):
        errors.append("advice.json: advice_cards must contain at least one card")


def check_evidence_refs(refs: list[Any], evidence_ids: set[str], path: str, errors: list[str]) -> None:
    if not refs:
        errors.append(f"{path}: must cite at least one evidence_id")
        return
    for ref in refs:
        if str(ref) not in evidence_ids:
            errors.append(f"{path}: unknown evidence_id {ref!r}")


def render_report(run_dir: Path) -> Path:
    validate_run(run_dir)
    manifest = read_json(run_dir / "run_manifest.json")
    badcase_dir = run_dir / "badcase_analysis"
    advice_dir = run_dir / "prompt_advice"
    advice = read_json(advice_dir / "advice.json")
    prompt_schema = read_json(advice_dir / "prompt_schema.json")
    evidence = read_jsonl(badcase_dir / "badcase_evidence.jsonl")
    section_attributions = read_jsonl(advice_dir / "prompt_section_attributions.jsonl")

    head_counts = Counter(row.get("head", "unknown") for row in evidence)
    section_counts = Counter()
    for row in section_attributions:
        for item in row.get("suspected_sections", []):
            section_counts[str(item.get("section", "unknown"))] += 1

    summary = advice.get("summary", {})
    top_heads = summary.get("top_heads") or [{"head": key, "count": count} for key, count in head_counts.most_common(5)]
    top_sections = summary.get("top_suspected_sections") or [
        {"section": key, "count": count} for key, count in section_counts.most_common(5)
    ]

    lines = [
        "# Prompt Badcase Advisor Report",
        "",
        "## One-line Conclusion",
        "",
        advice.get("one_line_conclusion")
        or "Review the advice cards below; they are diagnostic suggestions, not prompt patches.",
        "",
        "## Input Overview",
        f"- Prompt: `{manifest.get('prompt_path')}`",
        f"- Badcases: `{manifest.get('badcases_path')}`",
        f"- Taxonomy: `{manifest.get('taxonomy_path') or 'assets/default_taxonomy.yaml'}`",
        "",
        "## Summary",
        f"- Badcase count: {manifest.get('record_count', 0)}",
        f"- Evidence count: {len(evidence)}",
        f"- Main failure heads: {format_count_pairs(top_heads, 'head')}",
        f"- Most suspected prompt sections: {format_count_pairs(top_sections, 'section')}",
        "",
        "## Advice Cards",
        "",
    ]

    for card in advice.get("advice_cards", []):
        sections = ", ".join(str(item) for item in card.get("suspected_sections", []))
        lines.extend(
            [
                f"### {card.get('advice_id')}: {card.get('head')} -> {sections}",
                f"- Evidence: {', '.join(str(item) for item in card.get('evidence_ids', []))}",
                f"- Diagnosis: {card.get('diagnosis')}",
                f"- Suggestion: {card.get('suggestion')}",
                f"- Risk: {card.get('risk')}",
                f"- Confidence: {card.get('confidence')}",
                f"- Human questions: {'; '.join(str(item) for item in card.get('human_questions', []))}",
                "",
            ]
        )

    uncertainties = []
    for card in advice.get("advice_cards", []):
        uncertainties.extend(str(item) for item in card.get("uncertainties", []))
    lines.extend(
        [
            "## Uncertainty",
            "",
            *(f"- {item}" for item in (uncertainties or ["No additional uncertainties recorded."])),
            "",
            "## Appendix",
            "",
            "### Prompt Sections",
            "",
        ]
    )
    for section in prompt_schema.get("sections", []):
        lines.append(
            f"- `{section.get('section_id')}` lines {section.get('line_start')}-{section.get('line_end')}: {section.get('summary')}"
        )
    lines.extend(["", "### Evidence", ""])
    for item in evidence:
        lines.append(f"- `{item.get('evidence_id')}` {item.get('head')}: {item.get('quote')} ({item.get('why')})")
    lines.append("")

    report_path = advice_dir / "report.md"
    write_text(report_path, "\n".join(lines))
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--run-dir", required=True)
    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.command == "validate":
        validate_run(Path(args.run_dir))
        print(f"[validate] ok run_dir={args.run_dir}")
        return 0
    if args.command == "render":
        report = render_report(Path(args.run_dir))
        print(f"[render] wrote {report}")
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
