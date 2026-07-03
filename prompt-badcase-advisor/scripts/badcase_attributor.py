#!/usr/bin/env python3
"""Prepare and validate Badcase Attributor artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prompt_badcase_lib import (
    JSON,
    discover_prompt_sections,
    file_sha256,
    read_json,
    read_jsonl,
    read_text,
    rel_path,
    short_summary,
    stable_sha256,
    write_json,
    write_jsonl,
    write_text,
)

SCRIPT_VERSION = "prompt_badcase_advisor_v0"
TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".log"}
JSON_EXTENSIONS = {".json", ".jsonl"}
CSV_EXTENSIONS = {".csv"}

USER_FIELD_CANDIDATES = ("user", "input", "prompt", "question", "request")
ASSISTANT_FIELD_CANDIDATES = ("assistant", "output", "response", "answer", "actual", "completion")
LABEL_FIELD_CANDIDATES = ("label", "review_label", "verdict", "annotation", "human_label")
SCORE_FIELD_CANDIDATES = ("score", "overall", "dim_scores")
SPEAKER_RE = re.compile(r"^\s*(User|Human|Assistant|AI|用户|助手)\s*[:：]\s*(.*)$", re.IGNORECASE)

USER_AGENCY_RE = re.compile(
    r"\b(?:you|your)\s+(?:think|decide|realize|realise|say|ask|reply|reach|move|turn|feel|heart|hand|gaze)\b",
    re.IGNORECASE,
)
REPETITION_RE = re.compile(r"\b(\w{4,})\b(?:\W+\1\b){2,}", re.IGNORECASE)
ROLE_BREAK_RE = re.compile(r"\b(as an ai|language model|analysis|reasoning|rubric|evaluation)\b", re.IGNORECASE)
HARD_END_RE = re.compile(r"\b(story ends|scene ends|new scenario|reset|cannot continue|can't continue|refuse)\b", re.IGNORECASE)


def prepare_badcase_analysis(
    prompt: Path,
    badcases: Path,
    run_dir: Path,
    *,
    context: Path | None = None,
    taxonomy: Path | None = None,
    adapter: str = "auto",
    sample_size: int = 30,
    max_evidence_per_head: int = 20,
) -> JSON:
    run_id = run_dir.name
    prompt_text = read_text(prompt)
    analysis_dir = run_dir / "badcase_analysis"
    advice_dir = run_dir / "prompt_advice"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    advice_dir.mkdir(parents=True, exist_ok=True)

    files = expand_badcase_inputs(badcases)
    inventory_files: list[JSON] = []
    records: list[JSON] = []
    for file_path in files:
        parsed = parse_badcase_file(file_path, adapter=adapter)
        inventory_files.append(parsed["inventory"])
        records.extend(parsed["records"])

    samples = choose_samples(records, sample_size)
    rule_evidence = scan_rule_evidence(records, max_per_head=max_evidence_per_head)
    section_candidates = discover_prompt_sections(prompt_text)

    inventory = {
        "schema": "prompt_badcase_input_inventory_v1",
        "prompt_path": str(prompt.resolve()),
        "badcases_path": str(badcases.resolve()),
        "badcase_inputs": inventory_files,
        "sampling": {
            "max_records_sent_to_agent": sample_size,
            "strategy": "prefer_labeled_scored_long_and_diverse",
            "selected_count": len(samples),
        },
    }

    manifest = {
        "schema": "prompt_badcase_run_manifest_v1",
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "script_version": SCRIPT_VERSION,
        "prompt_path": str(prompt.resolve()),
        "prompt_sha256": file_sha256(prompt),
        "badcases_path": str(badcases.resolve()),
        "context_path": str(context.resolve()) if context else None,
        "taxonomy_path": str(taxonomy.resolve()) if taxonomy else None,
        "adapter": adapter,
        "sample_size": sample_size,
        "max_evidence_per_head": max_evidence_per_head,
        "record_count": len(records),
        "prompt_section_candidate_count": len(section_candidates),
    }

    write_json(run_dir / "run_manifest.json", manifest)
    write_json(analysis_dir / "input_inventory.json", inventory)
    write_jsonl(analysis_dir / "badcase_records.jsonl", records)
    write_jsonl(analysis_dir / "badcase_samples.jsonl", samples)
    write_jsonl(analysis_dir / "rule_evidence_candidates.jsonl", rule_evidence)
    write_json(advice_dir / "prompt_section_candidates.json", {"sections": section_candidates})
    write_text(run_dir / "assumptions.md", build_assumptions(inventory, section_candidates, taxonomy))
    write_text(analysis_dir / "agent_request_badcase_attributor.md", build_badcase_agent_request(run_dir))
    write_text(advice_dir / "agent_request_prompt_advisor.md", build_prompt_agent_request(run_dir))
    return manifest


def expand_badcase_inputs(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        raise FileNotFoundError(f"badcases path does not exist: {path}")
    files = [
        item
        for item in sorted(path.rglob("*"))
        if item.is_file() and item.suffix.lower() in TEXT_EXTENSIONS | JSON_EXTENSIONS | CSV_EXTENSIONS
    ]
    if not files:
        raise FileNotFoundError(f"no supported badcase files found under {path}")
    return files


def parse_badcase_file(path: Path, *, adapter: str = "auto") -> JSON:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        rows = read_jsonl(path)
        detected = detect_json_rows(rows)
        records = parse_json_rows(rows, path, detected)
    elif suffix == ".json":
        value = read_json(path)
        rows = value if isinstance(value, list) else [value]
        detected = detect_json_rows([row for row in rows if isinstance(row, dict)])
        records = parse_json_rows([row for row in rows if isinstance(row, dict)], path, detected)
    elif suffix == ".csv":
        records = parse_csv(path)
        detected = "csv"
    else:
        records, detected = parse_text(path)

    if adapter != "auto" and adapter not in detected:
        for record in records:
            record["parse_warnings"].append(f"requested adapter {adapter!r} did not match detected format {detected!r}")
            record["parse_confidence"] = min_confidence(record["parse_confidence"], "medium")

    return {
        "inventory": {
            "path": str(path.resolve()),
            "detected_format": detected,
            "record_count": len(records),
            "sample_count": min(5, len(records)),
            "confidence": format_confidence(detected),
        },
        "records": records,
    }


def detect_json_rows(rows: list[JSON]) -> str:
    if any("conversation" in row and ("scenario_id" in row or "dim_scores" in row) for row in rows):
        return "rpb-details-jsonl"
    if any(isinstance(row.get("messages"), list) for row in rows):
        return "openai-messages-json"
    return "generic-json"


def parse_json_rows(rows: list[JSON], path: Path, detected: str) -> list[JSON]:
    records: list[JSON] = []
    for index, row in enumerate(rows):
        if detected == "rpb-details-jsonl":
            record = parse_rpb_row(row, path, index)
        elif detected == "openai-messages-json":
            record = parse_messages_row(row, path, index)
        else:
            record = parse_generic_row(row, path, index)
        records.append(record)
    return records


def parse_rpb_row(row: JSON, path: Path, index: int) -> JSON:
    conversation = []
    warnings: list[str] = []
    for turn_index, turn in enumerate(row.get("conversation") or []):
        user, assistant = extract_turn_pair(turn)
        if not assistant:
            warnings.append(f"turn {turn_index} missing assistant/npc text")
        conversation.append({"turn": turn_index, "user": user, "assistant": assistant})
    case_id = f"{row.get('scenario_id', path.stem)}|run{row.get('run_id', 0)}|row{index}"
    return standard_record(
        case_id,
        "rpb",
        path,
        conversation,
        scores=extract_scores(row),
        labels=extract_labels(row),
        confidence="high" if conversation else "low",
        warnings=warnings,
        metadata={
            "scenario_id": row.get("scenario_id"),
            "run_id": row.get("run_id", 0),
            "prompt_version": row.get("prompt_version"),
            "row_index": index,
        },
    )


def parse_messages_row(row: JSON, path: Path, index: int) -> JSON:
    messages = row.get("messages") or []
    conversation: list[JSON] = []
    pending_user = ""
    system_messages: list[str] = []
    warnings: list[str] = []
    for message in messages:
        role = str(message.get("role", "")).lower()
        content = str(message.get("content", ""))
        if role == "system":
            system_messages.append(content)
        elif role == "user":
            pending_user = content
        elif role == "assistant":
            conversation.append({"turn": len(conversation), "user": pending_user, "assistant": content})
            pending_user = ""
    if not conversation:
        warnings.append("no user/assistant pairs found in messages")
    return standard_record(
        f"{path.stem}|messages|{index}",
        "openai_messages",
        path,
        conversation,
        scores=extract_scores(row),
        labels=extract_labels(row),
        confidence="high" if conversation else "low",
        warnings=warnings,
        metadata={"system_messages": system_messages, "row_index": index},
    )


def parse_generic_row(row: JSON, path: Path, index: int) -> JSON:
    user = first_present(row, USER_FIELD_CANDIDATES)
    assistant = first_present(row, ASSISTANT_FIELD_CANDIDATES)
    warnings: list[str] = []
    if assistant is None:
        assistant = json.dumps(row, ensure_ascii=False)
        warnings.append("no obvious assistant/output field; preserved row as assistant snippet")
    if user is None:
        user = ""
        warnings.append("no obvious user/input field")
    return standard_record(
        f"{path.stem}|row{index}",
        "generic_json",
        path,
        [{"turn": 0, "user": str(user), "assistant": str(assistant)}],
        scores=extract_scores(row),
        labels=extract_labels(row),
        confidence="medium" if not warnings else "low",
        warnings=warnings,
        metadata={"row_index": index},
    )


def parse_csv(path: Path) -> list[JSON]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [parse_generic_row(dict(row), path, index) | {"source": "csv"} for index, row in enumerate(rows)]


def parse_text(path: Path) -> tuple[list[JSON], str]:
    text = read_text(path)
    turns: list[JSON] = []
    current_role: str | None = None
    current_lines: list[str] = []
    chunks: list[tuple[str, str]] = []
    for line in text.splitlines():
        match = SPEAKER_RE.match(line)
        if match:
            if current_role:
                chunks.append((current_role, "\n".join(current_lines).strip()))
            current_role = normalize_role(match.group(1))
            current_lines = [match.group(2)]
        else:
            current_lines.append(line)
    if current_role:
        chunks.append((current_role, "\n".join(current_lines).strip()))

    pending_user = ""
    for role, content in chunks:
        if role == "user":
            pending_user = content
        elif role == "assistant":
            turns.append({"turn": len(turns), "user": pending_user, "assistant": content})
            pending_user = ""
    if turns:
        return [
            standard_record(
                f"{path.stem}|transcript",
                "transcript",
                path,
                turns,
                scores={},
                labels={},
                confidence="medium",
                warnings=[],
                metadata={},
            )
        ], "transcript-text"

    return [
        standard_record(
            f"{path.stem}|text",
            "plain_text",
            path,
            [{"turn": 0, "user": "", "assistant": text.strip()}],
            scores={},
            labels={},
            confidence="low",
            warnings=["no speaker labels found; treated whole file as assistant failure snippet"],
            metadata={},
        )
    ], "plain-text"


def standard_record(
    case_id: str,
    source: str,
    path: Path,
    conversation: list[JSON],
    *,
    scores: JSON,
    labels: JSON,
    confidence: str,
    warnings: list[str],
    metadata: JSON,
) -> JSON:
    return {
        "case_id": case_id,
        "source": source,
        "source_path": str(path.resolve()),
        "conversation": conversation,
        "scores": scores,
        "labels": labels,
        "parse_confidence": confidence,
        "parse_warnings": warnings,
        "metadata": metadata,
    }


def extract_turn_pair(turn: Any) -> tuple[str, str]:
    if not isinstance(turn, dict):
        return "", str(turn)
    user = first_present(turn, ("user", "user_message", "human", "input"))
    assistant = first_present(turn, ("assistant", "npc", "bot", "model", "output", "response"))
    return str(user or ""), str(assistant or "")


def first_present(row: JSON, fields: tuple[str, ...]) -> Any:
    for field in fields:
        if field in row and row[field] not in (None, ""):
            return row[field]
    return None


def extract_labels(row: JSON) -> JSON:
    return {key: row[key] for key in LABEL_FIELD_CANDIDATES if key in row}


def extract_scores(row: JSON) -> JSON:
    scores: JSON = {key: row[key] for key in SCORE_FIELD_CANDIDATES if key in row}
    for key, value in row.items():
        if key.endswith("_score"):
            scores[key] = value
    return scores


def normalize_role(role: str) -> str:
    role = role.lower()
    if role in {"user", "human", "用户"}:
        return "user"
    return "assistant"


def format_confidence(detected: str) -> str:
    return "high" if detected in {"rpb-details-jsonl", "openai-messages-json"} else "medium"


def min_confidence(left: str, right: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return left if order.get(left, 0) <= order.get(right, 0) else right


def choose_samples(records: list[JSON], sample_size: int) -> list[JSON]:
    def score(record: JSON) -> tuple[int, int, int]:
        has_label = 1 if record.get("labels") else 0
        has_score = 1 if record.get("scores") else 0
        length = sum(len(turn.get("assistant", "")) for turn in record.get("conversation", []))
        return (has_label + has_score, length, -len(record.get("parse_warnings", [])))

    return sorted(records, key=score, reverse=True)[:sample_size]


def scan_rule_evidence(records: list[JSON], *, max_per_head: int) -> list[JSON]:
    evidence: list[JSON] = []
    counts: Counter[str] = Counter()
    patterns = [
        ("USER_AGENCY_VIOLATION", "critical", USER_AGENCY_RE, "assistant may be narrating user agency"),
        ("ROLE_OR_FORMAT_BREAK", "high", ROLE_BREAK_RE, "assistant may be leaving role or output format"),
        ("REFUSAL_OR_HARD_END", "high", HARD_END_RE, "assistant may be refusing, resetting, or ending hard"),
        ("REPETITION_OR_STASIS", "high", REPETITION_RE, "assistant may be repeating phrasing"),
    ]
    for record in records:
        for turn in record.get("conversation", []):
            assistant = str(turn.get("assistant", ""))
            for head, severity, pattern, why in patterns:
                if counts[head] >= max_per_head:
                    continue
                match = pattern.search(assistant)
                if not match:
                    continue
                counts[head] += 1
                evidence.append(
                    {
                        "evidence_id": f"R{len(evidence) + 1:04d}",
                        "case_id": record["case_id"],
                        "head": head,
                        "severity": severity,
                        "turn": turn.get("turn", 0),
                        "quote": quote_around(assistant, match.start()),
                        "why": why,
                        "confidence": "medium",
                        "source": "rule_candidate",
                    }
                )
    return evidence


def quote_around(text: str, pos: int, width: int = 180) -> str:
    start = max(0, pos - width // 2)
    end = min(len(text), pos + width // 2)
    return short_summary(text[start:end], width)


def build_assumptions(inventory: JSON, sections: list[JSON], taxonomy: Path | None) -> str:
    formats = ", ".join(
        f"{Path(item['path']).name}:{item['detected_format']}" for item in inventory.get("badcase_inputs", [])
    )
    low_sections = [section["name"] for section in sections if section.get("confidence") == "low"]
    lines = [
        "# Prompt Badcase Advisor Assumptions",
        "",
        "- Badcase formats were inferred by file shape and field names.",
        f"- Detected inputs: {formats or 'none'}.",
        "- Prompt section boundaries are deterministic candidates for Codex review.",
        f"- Low-confidence prompt sections: {', '.join(low_sections) if low_sections else 'none'}.",
        f"- Taxonomy source: {taxonomy if taxonomy else 'assets/default_taxonomy.yaml'}; Codex may refine it.",
        "- Agent outputs must preserve uncertainty rather than upgrading inference to fact.",
        "",
    ]
    return "\n".join(lines)


def build_badcase_agent_request(run_dir: Path) -> str:
    return f"""# Badcase Attributor Request

Read this run directory: `{run_dir}`.

Produce:
- `badcase_analysis/task_understanding.json`
- `badcase_analysis/badcase_schema.json`
- `badcase_analysis/failure_taxonomy.json`
- `badcase_analysis/badcase_evidence.jsonl`
- `badcase_analysis/badcase_attributions.jsonl`
- `badcase_analysis/badcase_report.md`

Follow `prompt-badcase-advisor/references/workflow.md` and
`prompt-badcase-advisor/references/output-contracts.md`. This stage must explain
what is wrong with the badcases and must not recommend prompt edits.
"""


def build_prompt_agent_request(run_dir: Path) -> str:
    return f"""# Prompt Advisor Request

Read this run directory after Badcase Attributor outputs exist: `{run_dir}`.

Produce:
- `prompt_advice/prompt_schema.json`
- `prompt_advice/prompt_section_attributions.jsonl`
- `prompt_advice/advice.json`

Then run:
`python3 prompt-badcase-advisor/scripts/prompt_badcase_advisor.py validate --run-dir {run_dir}`
and render the report if validation passes.

Follow `prompt-badcase-advisor/references/workflow.md` and
`prompt-badcase-advisor/references/output-contracts.md`. Advice must cite
evidence and prompt sections, keep uncertainty, and set `not_a_patch: true`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--badcases", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--context")
    parser.add_argument("--taxonomy")
    parser.add_argument("--adapter", default="auto")
    parser.add_argument("--sample-size", type=int, default=30)
    parser.add_argument("--max-evidence-per-head", type=int, default=20)
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(args.output_dir or f"results/prompt_badcase_advisor/{run_id}")
    manifest = prepare_badcase_analysis(
        Path(args.prompt),
        Path(args.badcases),
        run_dir,
        context=Path(args.context) if args.context else None,
        taxonomy=Path(args.taxonomy) if args.taxonomy else None,
        adapter=args.adapter,
        sample_size=args.sample_size,
        max_evidence_per_head=args.max_evidence_per_head,
    )
    print(f"[prepare] run_dir={run_dir}")
    print(f"[prepare] records={manifest['record_count']} sections={manifest['prompt_section_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
