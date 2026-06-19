---
name: skill-maintenance
description: Audit and maintain an agent skills repository. Use when the user asks to improve, lint, split, evaluate, index, vendor, or maintain skills, SKILL.md files, routing descriptions, gotchas, scripts, references, or the skills README.
---

# Skill Maintenance

Use this skill to keep a skills repository small, routable, executable, and safe.

## Workflow

1. Inspect the repository state before editing:
   - `git status --short`
   - `find . -maxdepth 2 -name SKILL.md | sort`
   - `python3 skill-maintenance/scripts/lint-skills.py`
2. Treat each `description` as a routing rule, not a marketing summary.
3. Keep each `SKILL.md` as a hub:
   - trigger conditions
   - required setup or stop rules
   - high-signal gotchas
   - pointers to conditional files
4. Move heavy conditional content out of `SKILL.md`:
   - `references/` for detailed workflows, API or CLI notes, and gotchas
   - `scripts/` or `bin/` for deterministic checks, extraction, validation, or setup
   - `assets/` for templates and output schemas
   - `examples/` for concrete input/output examples
5. Update `evals/skill-routing.yaml` when a description changes or when a skill loads incorrectly.
6. Update `README.md` only after the skill list, status, and vendoring surface are clear.
7. Run validation before claiming completion.

## Feedback Improvement Loop

When the user critiques an agent's own skill behavior, routing, output format, validation discipline, or repeated mistakes:

1. Read the relevant `SKILL.md`, support files, README/index entries, and routing evals before proposing changes.
2. Convert the feedback into the smallest repo-local artifact that prevents recurrence: skill text, reference gotcha, script/check, or routing eval.
3. If the user asked for ideas only, report the proposed diff shape and wait. If the user asked to change it, edit directly.
4. Validate the change and report the exact writeback added.

## Heuristics

- If the agent would recreate the same parsing, validation, or formatting code every run, add a script.
- If content is only needed for one branch, put it behind a reference file.
- If a behavior came from a real failure, preserve it as a gotcha with symptom, cause, and fix.
- If a skill is broad enough to trigger on unrelated requests, tighten the description and add negative routing evals.
- If a skill is rarely selected despite matching real requests, add the user's actual phrasing to the description and positive routing evals.
- If a skill is mostly a long checklist, look for the deterministic pieces that should become scripts.

## Validation

Run:

```bash
python3 skill-maintenance/scripts/lint-skills.py
```

When changing vendored skills, also run:

```bash
uv run --project ../skift skift status
uv run --project ../skift skift update --check
```
