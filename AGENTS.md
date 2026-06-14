# Praxis Agent Operating Protocol

This repository is the source of truth for reusable agent skills.

Treat each skill as infrastructure: a durable, routable, testable workflow that
future agents can reuse.

## Repository Scope

Praxis maintains:

- skill source files and bundled resources
- skill routing descriptions
- repository-level indexes and routing evals
- deterministic maintenance and validation scripts
- vendored-skill tracking

## Operating Principles

- Read the current repo surface before changing it. Use `rg`, `find`, `git
  status --short`, and nearby docs rather than relying on memory alone.
- Prefer executable checks, small scripts, and routing evals over prose-only
  rules when behavior can be tested.
- Keep work grounded in real failures, real user phrasing, and real workflows.
  Abstract advice is only useful after it becomes an artifact agents can follow.
- Preserve user and generated work you did not create. Do not revert unrelated
  changes.
- Treat every completion claim as a contract. Run the relevant validation or say
  clearly what was not run.

## Skill Design Rules

Each `SKILL.md` should be a small routing hub:

- clear trigger conditions
- stop rules and required setup
- high-signal gotchas
- pointers to conditional support files

Move heavy material out of `SKILL.md`:

- `references/` for detailed workflows, API notes, checklists, and gotchas
- `scripts/` or `bin/` for deterministic checks, extraction, validation, or
  setup
- `assets/` for templates, schemas, and reusable files
- `examples/` for concrete inputs and outputs

Descriptions are routing rules, not marketing copy. If a description is too
broad, tighten it and add negative routing evals. If a skill fails to trigger on
real user wording, add that wording to the description and positive routing
evals.

## Skill Lifecycle

When creating or changing a skill:

1. Define the behavior boundary: what should load this skill, what should not,
   and what artifact or outcome proves it worked.
2. Update the skill hub and any conditional support files.
3. Add deterministic helpers when the same parsing, validation, or formatting
   logic would otherwise be recreated by agents.
4. Update `README.md` when the visible skill inventory changes.
5. Update `evals/skill-routing.yaml` when routing behavior changes or when a
   real misroute is discovered.
6. If the skill is vendored, keep `skift.toml` and `skift.lock` aligned and
   review the vendor diff.
7. Run validation before reporting success.

## Validation Commands

Use these checks for skills-repo maintenance:

```bash
git status --short
find . -maxdepth 2 -name SKILL.md | sort
python3 skill-maintenance/scripts/lint-skills.py
git diff --check
```

For vendored-skill work, also run:

```bash
uv run --project ../skift skift status
uv run --project ../skift skift update --check
```

If a Python path fails because system Python lacks `yaml`, use the proven local
pattern:

```bash
uv run --with pyyaml python <script>
```

## Skill Improvement Loop

Every substantial repository change should follow this loop:

1. State the repo-local objective and success signal.
2. Inspect the relevant `SKILL.md`, support directories, `README.md`, routing
   evals, and vendoring files.
3. Make the smallest useful edit.
4. Validate with the relevant repo checks.
5. Write back reusable learning as one of:
   - skill change
   - routing eval
   - script or check
   - reference gotcha with symptom, cause, and fix
   - backlog item for a future skill split

## Praxis Maintenance Checks

Use these concrete checks when reviewing or changing skills:

- Routing: Does the `description` say exactly when to use the skill? Does it
  avoid catching adjacent requests?
- Progressive disclosure: Is `SKILL.md` still a hub, or has it become a long
  manual that belongs in `references/`?
- Resource linkage: If `references/`, `scripts/`, `assets/`, or `examples/`
  exist, does `SKILL.md` point to them?
- Executability: Is repeated deterministic logic captured as a script rather
  than re-described in prose?
- Indexing: Does `README.md` reflect the visible skill inventory?
- Routing evals: Did description changes or real routing misses update
  `evals/skill-routing.yaml`?
- Vendoring: Are `skift.toml`, `skift.lock`, and vendored files consistent?
- Diff hygiene: Are unrelated user changes left untouched?

## Completion Standard

Before finishing a task in this repo, report:

- files changed
- validation run, with any skipped checks called out
- any repo-local writeback added, such as evals, scripts, references, or README
  changes
- any follow-up that is genuinely useful

If nothing was changed, say that plainly and explain what was inspected.
