#!/usr/bin/env python3
"""Wrapper CLI for the Prompt Badcase Advisor skill."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from badcase_attributor import prepare_badcase_analysis
from prompt_badcase_lib import read_json, read_jsonl, write_json, write_jsonl, write_text
from prompt_advisor import render_report, validate_run

SKILL_DIR = Path(__file__).resolve().parents[1]
FIXTURES = SKILL_DIR / "assets" / "fixtures"


def default_run_dir() -> Path:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path("results") / "prompt_badcase_advisor" / run_id


def prepare_command(args: argparse.Namespace) -> int:
    run_dir = Path(args.output_dir) if args.output_dir else default_run_dir()
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
    print("[prepare] next: fill agent outputs, then run validate and render")
    return 0


def validate_command(args: argparse.Namespace) -> int:
    validate_run(Path(args.run_dir))
    print(f"[validate] ok run_dir={args.run_dir}")
    return 0


def render_command(args: argparse.Namespace) -> int:
    report = render_report(Path(args.run_dir))
    print(f"[render] wrote {report}")
    return 0


def self_test_command(_: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(prefix="prompt-badcase-advisor-") as tmp:
        tmp_path = Path(tmp)
        badcases_dir = tmp_path / "badcases"
        badcases_dir.mkdir()
        shutil.copy(FIXTURES / "rpb-details.jsonl", badcases_dir / "rpb-details.jsonl")
        shutil.copy(FIXTURES / "openai-messages.json", badcases_dir / "openai-messages.json")
        shutil.copy(FIXTURES / "transcript.txt", badcases_dir / "transcript.txt")
        prompt_path = FIXTURES / "sectioned-prompt.md"
        run_dir = tmp_path / "run"

        manifest = prepare_badcase_analysis(prompt_path, badcases_dir, run_dir, sample_size=10)
        seed_agent_outputs(run_dir)
        validate_run(run_dir)
        report = render_report(run_dir)

        plain_run = tmp_path / "plain-run"
        prepare_badcase_analysis(FIXTURES / "unsectioned-prompt.md", badcases_dir, plain_run, sample_size=5)
        candidates = read_json(plain_run / "prompt_advice" / "prompt_section_candidates.json")["sections"]
        if not candidates or candidates[0]["confidence"] != "low":
            raise SystemExit("self-test failed: unsectioned prompt should produce low-confidence sections")

        print(f"[self-test] ok records={manifest['record_count']} report={report}")
    return 0


def seed_agent_outputs(run_dir: Path) -> None:
    badcase_dir = run_dir / "badcase_analysis"
    advice_dir = run_dir / "prompt_advice"
    manifest = read_json(run_dir / "run_manifest.json")
    records = read_jsonl(badcase_dir / "badcase_records.jsonl")
    rule_evidence = read_jsonl(badcase_dir / "rule_evidence_candidates.jsonl")
    evidence = [
        {
            "evidence_id": "E001",
            "case_id": rule_evidence[0]["case_id"] if rule_evidence else records[0]["case_id"],
            "head": rule_evidence[0]["head"] if rule_evidence else "REPETITION_OR_STASIS",
            "severity": rule_evidence[0]["severity"] if rule_evidence else "high",
            "quote": rule_evidence[0]["quote"] if rule_evidence else records[0]["conversation"][0]["assistant"],
            "why": rule_evidence[0]["why"] if rule_evidence else "fixture evidence",
            "confidence": "medium",
        }
    ]
    sections = read_json(advice_dir / "prompt_section_candidates.json")["sections"]
    section = sections[0]

    write_json(
        badcase_dir / "task_understanding.json",
        {
            "task_summary": "Generate immersive role-play replies.",
            "target_output": {"format": "short narrative reply"},
            "quality_goals": ["advance the scene", "preserve user agency"],
            "hard_constraints": ["do not speak for the user"],
            "confidence": "medium",
            "uncertainties": ["Fixture prompt is intentionally small."],
        },
    )
    write_json(
        badcase_dir / "badcase_schema.json",
        {
            "record_format": "mixed fixture files",
            "conversation_fields": {"conversation": "conversation"},
            "human_labels": [],
            "score_fields": ["dim_scores", "overall"],
            "metadata_fields": ["scenario_id", "run_id"],
            "confidence": "medium",
            "warnings": [],
        },
    )
    write_json(
        badcase_dir / "failure_taxonomy.json",
        {
            "heads": [
                {
                    "id": "REPETITION_OR_STASIS",
                    "label": "Repetition or stasis",
                    "severity": "high",
                    "definition": "Repeated phrasing or stalled scene movement.",
                    "source": "fixture",
                }
            ],
            "uncertainties": ["Fixture taxonomy is minimal."],
        },
    )
    write_jsonl(badcase_dir / "badcase_evidence.jsonl", evidence)
    write_jsonl(
        badcase_dir / "badcase_attributions.jsonl",
        [
            {
                "case_id": evidence[0]["case_id"],
                "heads": [
                    {
                        "head": evidence[0]["head"],
                        "severity": evidence[0]["severity"],
                        "confidence": "medium",
                        "reason": "Fixture evidence indicates a hard failure pattern.",
                        "evidence_ids": ["E001"],
                    }
                ],
                "uncertainties": ["Fixture evidence is intentionally tiny."],
            }
        ],
    )
    write_text(
        badcase_dir / "badcase_report.md",
        "# Badcase Report\n\nFixture report: evidence indicates a reviewable failure pattern.\n",
    )
    write_json(advice_dir / "prompt_schema.json", {"sections": sections, "uncertainties": []})
    write_jsonl(
        advice_dir / "prompt_section_attributions.jsonl",
        [
            {
                "case_id": evidence[0]["case_id"],
                "head": evidence[0]["head"],
                "evidence_ids": ["E001"],
                "suspected_sections": [
                    {
                        "section": section["section_id"],
                        "confidence": "medium",
                        "reason": "Fixture prompt section may influence the observed failure.",
                    }
                ],
            }
        ],
    )
    write_json(
        advice_dir / "advice.json",
        {
            "schema": "prompt_badcase_advice_v1",
            "run_id": manifest["run_id"],
            "summary": {
                "badcase_count": manifest["record_count"],
                "evidence_count": 1,
                "top_heads": [{"head": evidence[0]["head"], "count": 1}],
                "top_suspected_sections": [{"section": section["section_id"], "count": 1}],
            },
            "advice_cards": [
                {
                    "advice_id": "A001",
                    "head": evidence[0]["head"],
                    "priority": "high",
                    "suspected_sections": [section["section_id"]],
                    "evidence_ids": ["E001"],
                    "diagnosis": "The prompt may not sufficiently prevent the failure pattern.",
                    "suggestion": "Review the cited section and consider a more explicit behavioral constraint.",
                    "risk": "Could make the style more constrained.",
                    "human_questions": ["Is this failure type always unacceptable for the product?"],
                    "confidence": "medium",
                    "uncertainties": ["Fixture run does not represent a real product distribution."],
                    "not_a_patch": True,
                }
            ],
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--prompt", required=True)
    prepare.add_argument("--badcases", required=True)
    prepare.add_argument("--output-dir")
    prepare.add_argument("--context")
    prepare.add_argument("--taxonomy")
    prepare.add_argument("--adapter", default="auto")
    prepare.add_argument("--sample-size", type=int, default=30)
    prepare.add_argument("--max-evidence-per-head", type=int, default=20)
    prepare.set_defaults(func=prepare_command)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--run-dir", required=True)
    validate.set_defaults(func=validate_command)

    render = subparsers.add_parser("render")
    render.add_argument("--run-dir", required=True)
    render.set_defaults(func=render_command)

    self_test = subparsers.add_parser("self-test")
    self_test.set_defaults(func=self_test_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    commands = {"prepare", "validate", "render", "self-test", "-h", "--help"}
    if argv and argv[0] not in commands:
        argv.insert(0, "prepare")
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
