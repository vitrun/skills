# Agent Skills

A collection of agent skills that extend capabilities across planning, development, and tooling.

## Planning & Design

These skills help you think through problems before writing code.

- **brainstorming** — Explore intent, requirements, and design before implementation.
- **write-a-prd** — Create a PRD through an interactive interview, codebase exploration, and module design. Filed as a GitHub issue.
- **prd-to-plan** — Turn a PRD into tracer-bullet vertical slices saved as a local plan.
- **request-refactor-plan** — Create a detailed refactor plan with tiny commits and file it as a GitHub issue.
- **grill-me** — Get relentlessly interviewed about a plan or design until every branch of the decision tree is resolved.
- **design-an-interface** — Generate radically different module/interface designs for comparison.
- **ubiquitous-language** — Extract and normalize a DDD-style glossary from the conversation.
- **route-driven-work** — Convert route-clear coding goals into durable work routes with slice scratchpads, validation, guardrails, and commit discipline.
- **frontier-search** — Search experiment axes for better Pareto frontiers before choosing an implementation route.
- **prompt-badcase-advisor** — Diagnose prompt badcases with evidence-backed attribution and human-reviewable advice, without auto-applying prompt patches.
- **harden-preference-data** — Design shortcut-resistant DPO/RLHF/RLAIF preference data with same-context hard negatives and utility validation.
- **deli-autoresearch** — Protocol framework for unattended long-horizon autonomous research runs with file-backed state, stall detection, and heartbeat watchdogs.
- **programmable-doc-review** — Audit and tighten technical docs until coding agents can implement them consistently, with clear agent-fill vs human-escalation boundaries.
- **perspective-context** — Reshape large mixed materials into a focused intermediate representation before audit, diagnosis, or improvement.

## Development

These skills help you write, refactor, and fix code.

- **tdd** — Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time.
- **systematic-debugging** — Investigate bugs, failures, and unexpected behavior by tracing root cause before fixes.
- **verification-before-completion** — Require fresh verification evidence before claiming work is complete, fixed, or passing.
- **local-production-validation** — Design local validation that exercises the real production-shaped component surface with local/mock adapters instead of internal calls.
- **receiving-code-review** — Evaluate review feedback technically before implementing it.
- **finishing-a-development-branch** — Verify, choose an integration path, and safely finish a branch or worktree.
- **improve-codebase-architecture** — Explore a codebase for architectural improvement opportunities, focusing on deepening shallow modules and improving testability.
- **using-git-worktrees** — Create or detect isolated git worktrees for feature work.

## Tooling & Setup

- **setup-pre-commit** — Set up Husky pre-commit hooks with lint-staged, Prettier, type checking, and tests.
- **git-guardrails-claude-code** — Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, etc.) before they execute.
- **skill-maintenance** — Audit and maintain this skills repository: routing descriptions, file splitting, gotchas, scripts, README indexing, and vendored-skill checks.
- **cloud-gpu-runner** — Use GCP/AWS GPU resources efficiently with artifact staging, Spot resumability, cost/capacity checks, and cleanup discipline.

## Hiring & Interviews

- **engineering-interview** — Run staged engineering interview workflows: resume analysis and questioning, Q&A organization, and JD-aligned assessment.

## Vendored Skills

External skills are tracked in `skift.toml` and locked in `skift.lock`.

```bash
uv run --project ../skift skift status
uv run --project ../skift skift update --check
```

Use `uv run --project ../skift skift inspect <repo>` to discover upstream skills and `uv run --project ../skift skift add <repo>//<path>` to track a single skill. Review the resulting diff before committing updates.

## Maintenance Checks

```bash
python3 skill-maintenance/scripts/lint-skills.py
```

Routing examples live in `evals/skill-routing.yaml`. Update them when a skill description changes or when a skill loads incorrectly.

Current tracked upstreams:

- **redesign-skill** — `git@github.com:Leonxlnx/taste-skill.git//skills/redesign-skill`
- **taste-skill** — `git@github.com:Leonxlnx/taste-skill.git//skills/taste-skill`
- **systematic-debugging** — `git@github.com:obra/superpowers.git//skills/systematic-debugging`
- **verification-before-completion** — `git@github.com:obra/superpowers.git//skills/verification-before-completion`
- **receiving-code-review** — `git@github.com:obra/superpowers.git//skills/receiving-code-review`
- **finishing-a-development-branch** — `git@github.com:obra/superpowers.git//skills/finishing-a-development-branch`
- **deli-autoresearch** — `https://github.com/victorchen96/victorchen96.github.io.git//auto_research/framework.html`

## Research & Feeds

- **paper-reader** — Read, explain, and critique a single research paper.
- **paper-digest** — Fetch, filter, summarize, and optionally publish recent AI/ML paper roundups.
- **paper-patterns** — Extract reusable research patterns from papers and maintain an OKF-style pattern library.
- **x-feed-capture** — Capture, filter, summarize, and optionally publish high-value X/Twitter feed updates.

## Writing Skills

- **edit-article** — Restructure and tighten article drafts.
- **write-a-skill** — Create new skills with proper structure, progressive disclosure, and bundled resources.
