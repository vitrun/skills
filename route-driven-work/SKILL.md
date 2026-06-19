---
name: route-driven-work
description: Convert clear outcome-driven coding goals into route-driven autonomous work, then execute or continue them with per-slice scratchpads, validation, and commit discipline. Use when the target is stable enough to plan as a route with repeatable evidence. Do not use for open-ended SOTA, experiment-space, or Pareto frontier search; use frontier-search instead.
---

# Route Driven Work

Use this skill as the workflow for route-clear autonomous coding tasks. The defining feature is not elapsed time; it is that the desired outcome is stable enough to write a route, decompose workstreams, validate progress, and preserve state between slices. Match the user's language in outputs.

Use `frontier-search` instead when the main task is to discover which technical direction, experiment axis, or Pareto tradeoff is best. Use `deli-autoresearch` only when the user explicitly asks for unattended orchestration, watchdogs, heartbeat checks, or the Deli AutoResearch protocol.

Route-driven work has a default git discipline: choose a commit cadence that fits the route, and before every commit run a review-fix loop until issues converge. Do this even when the user does not explicitly ask for it.

Choose the mode from the request:

- `evaluate`: assess a goal/spec and, if suitable, produce a route document. Do not create a scratchpad yet.
- `execute`: start working from a route document. Create one scratchpad for the first active slice, then work autonomously.
- `continue`: resume interrupted work. Read the route and the active slice scratchpad, then continue from recorded state.

If the user only provides a new goal/spec, default to `evaluate`. If the user says "start", "execute", "run this route", or similar, use `execute`. If the user says "continue", "resume", "pick up", "context cleared", or similar, use `continue`.

## Goal Boundary And Stop Discipline

In `execute` and `continue` mode, the route's `Whole Goal` is the default completion target. The `First Autonomous Slice` is an early checkpoint for validation and commit discipline, not permission to stop the route-driven run.

The route's `Whole Goal Checklist` is the authoritative progress view. Keep it near the top of the route, update it at every slice boundary, and use only these status values:

- `done`: completed with linked evidence.
- `doing`: actively being worked now.
- `todo`: not started and not blocked.
- `blocked`: cannot continue without specific user input or external state change.
- `deferred`: explicitly out of the current route or approved later.

Stop at a slice boundary only when the user's request explicitly limits the run to that slice or named workstream. Otherwise, closing a slice means:

1. Consolidate durable findings and evidence into the route.
2. Update the `Whole Goal Checklist`.
3. Close the current slice scratchpad.
4. Choose the next highest-value unblocked `todo`/`doing` checklist item or workstream from the route.
5. Create a new scratchpad for the next slice and continue execution.

Before ending an `execute` or `continue` run, perform a Stop Audit against the `Whole Goal Checklist`:

1. If any `doing` or `todo` checklist item remains and is not covered by a stop rule or explicit user scope limit, continue with the next highest-value item.
2. If an item is `blocked`, record the exact blocker, attempts made, and required user decision or external state change.
3. If an item is `deferred`, record why it is outside the current route.
4. If all non-deferred items are `done`, run the route's final validation before declaring the Whole Goal complete.

Do not end the turn merely because the first slice, active slice, or a P0 workstream is validated. End only when:

- the `Whole Goal` is complete and validated;
- the user explicitly asked for only a slice/workstream and that scoped target is complete;
- a stop rule triggers;
- the user interrupts or redirects the run;
- a genuine blocker requires user input after reasonable investigation.

If stopping before the `Whole Goal`, state the exact stop rule, user-scoped target, interruption, or blocker. If none applies, keep going into the next slice.

## Mode: Evaluate

Evaluate whether the source task is suitable for route-driven autonomous work.

Classify it as:

- `Suitable`: convert it into a route.
- `Needs reframing`: explain what is missing, then provide a reframed route if reasonable assumptions can make it executable.
- `Not suitable`: explain why and suggest a normal shorter prompt or minimum changes needed.

Prefer `Suitable` when most are true:

- The goal is valuable, non-trivial, and likely to take more than 30-60 minutes.
- Success can be measured by tests, benchmarks, profiles, screenshots, static checks, logs, error rates, migration counts, or other repeatable evidence.
- The path may need local investigation, but the desired outcome and route shape are clear enough to plan.
- The agent can inspect the repo, run commands, make incremental changes, and verify results locally or in a safe test environment.
- Boundaries, non-goals, safety rules, and rollback expectations can be written down.
- Progress can be preserved outside context.
- The work can be decomposed into small commits or reversible experiments.

Prefer `Needs reframing` when:

- The goal is broad but measurable after adding metrics or acceptance criteria.
- The task is currently a fixed checklist, but can be reframed around an outcome.
- The repo has weak validation, but the first slice can create the validation harness.
- Product tradeoffs exist but can be isolated behind stop rules.

Prefer `Not suitable` when:

- The task is a small feature or bug fix that should be done directly.
- The goal depends mainly on subjective taste, product judgment, negotiation, or user feedback.
- The agent cannot verify progress without external production systems, credentials, manual QA, or user decisions.
- The work is destructive, security-sensitive, legal/financial/medical high stakes, or likely to touch user data without clear approvals.
- The task requires frequent human decisions or live operational access.
- The requested outcome is so vague that an agent would invent success criteria.
- The core work is SOTA discovery, experiment-axis search, or finding a better Pareto frontier before a route can be chosen.

### Evaluate Output

Produce:

1. `Fit Assessment`
2. `Route Document`
3. `How To Start`
4. `Open Questions Or Assumptions`

If working in a repo or file-producing context, write only the route file during evaluate. Prefer:

- `docs/work-route-<slug>.md`
- or a specific scoped path such as `docs/work-route-janus-image-api.md`

Do not create a scratchpad during evaluate. Scratchpads belong to execution state and are created only when `execute` or `continue` starts a slice. The route must name the scratchpad naming pattern.

The route must include a `Commit Plan` that chooses a cadence, names commit boundaries, and requires the pre-commit review-fix loop.

In `How To Start`, tell the user simply:

```text
This route is ready. Optionally clear context, then ask Codex to use route-driven-work to execute <route-path>.
```

## Mode: Execute

Use this when the user asks to start or execute a route.

Steps:

1. Locate the route document from the user's path or common names such as `docs/work-route-*.md`, with `docs/long-horizon-route-*.md` supported only as a legacy name.
2. Read the route and relevant source/spec if referenced.
3. Inspect `git status`.
4. Select the first active slice from the route.
5. Create a scratchpad for that slice using the route's naming pattern, normally `docs/work-scratchpad-<slug>-<slice-id>.md`, and set the route's `Active Scratchpad` to that path.
6. Initialize the scratchpad as local working memory for that slice with slice state, local tasks, current hypothesis, recent evidence, temporary findings, blockers, review-fix notes, and next actions.
7. Choose and record the commit cadence for the active slice if the route does not already specify one.
8. Execute the first autonomous slice from the route.
9. Work in evidence-driven cycles:
   - choose the highest-value executable task;
   - state the hypothesis and done condition in the scratchpad;
   - establish or reuse baseline;
   - make the smallest reversible change;
   - run validation;
   - compare before/after behavior;
   - update the scratchpad;
   - run the review-fix loop before any commit;
   - commit logically when validated and review-clean.
10. When the active slice closes, consolidate durable results into the route, update the `Whole Goal Checklist`, and mark the scratchpad closed.
11. Run the Stop Audit. If the `Whole Goal` is not complete and no stop rule or user-scoped slice limit applies, choose the next highest-value unblocked `todo`/`doing` checklist item or workstream, create a new scratchpad for that slice, and continue the same cycle.
12. Stop only when the `Whole Goal` is complete, the explicitly requested slice/workstream is complete, a stop rule triggers, or the user interrupts.

## Mode: Continue

Use this when the user asks to resume after interruption, context clearing, or an earlier route-driven run.

Steps:

1. Locate the route document:
   - use the user's explicit path, or
   - search common route names such as `docs/work-route-*.md`, with `docs/long-horizon-route-*.md` supported only as a legacy name, or
   - ask only if multiple plausible routes exist and choosing one would be risky.
2. Locate the active scratchpad from the route:
   - use the route's active scratchpad path if present, or
   - create a scratchpad for the current `doing` slice if the route has no active scratchpad yet, or
   - ask only if route state conflicts and choosing a slice would be risky.
3. Read route and scratchpad before relying on any chat memory.
4. Inspect `git status` and recent commits.
5. Resume the highest-value unblocked task in the active slice.
6. Resume or choose the commit cadence for the active slice and preserve any pending review-fix state from the scratchpad.
7. If the scratchpad says the active slice is closed, consolidate any remaining durable findings into the route, update the `Whole Goal Checklist`, then choose the next slice from the route using evidence, risk, and stop rules.
8. If a slice closes during resumed work, repeat the same consolidation and next-slice handoff unless the Stop Audit shows the `Whole Goal` is complete, a stop rule triggers, or the user explicitly scoped the request to that slice.
9. Continue the same evidence-driven cycle as execute mode.

If the active scratchpad is missing, do not invent prior temporary state. Create a fresh scratchpad for the route's current active slice and continue from the durable route state.

## Route And Scratchpad Memory Model

Use exactly two artifact types:

- `work-route-<slug>.md` is durable project memory. It stores the strategy, stable findings, completed slice summaries, verified results, durable decisions, disproven hypotheses, updated risks, deferred work, and next slices.
- `work-scratchpad-<slug>-<slice-id>.md` is temporary working memory for one slice. It stores only the state needed to resume that slice: local tasks, current hypothesis, recent evidence, temporary findings, blockers, review-fix notes, and next actions.

Legacy `long-horizon-route-*` and `long-horizon-scratchpad-*` artifacts may exist from older runs. Read and continue them when referenced, but prefer the `work-*` names for new routes and scratchpads.

The route is the index: its `Active Scratchpad` section records the current scratchpad path or `none`.

Keep the scratchpad concise and local to its slice. Avoid raw command noise unless it is evidence. It may reference route checklist or workstream IDs, but it must not copy the `Whole Goal Checklist` or the full `Workstreams` list.

At the end of each slice, run consolidation:

1. Distill durable findings, results, decisions, risks, deferrals, and next-slice recommendations from the scratchpad into the route.
2. Mark the active slice closed in the route with evidence.
3. Update the `Whole Goal Checklist` so the next unblocked `todo`/`doing` item is obvious.
4. Mark the scratchpad `closed`, stop appending to it, and set the route's `Active Scratchpad` to `none`.
5. Create a fresh scratchpad for the next slice only when execution continues.

## Commit Cadence And Standards

Every route should include a commit plan. If the user asks the agent to choose the cadence, choose it without asking.

Pick the smallest cadence that keeps history reviewable and reversible:

- `per validated workstream`: default for most multi-hour routes; commit when a Wxx workstream or coherent sub-workstream is validated and documented.
- `per vertical slice`: use when several Wxx items must land together to produce a working behavior.
- `per harness/baseline then implementation`: use when validation infrastructure must be separated from behavior changes.
- `spike branch only`: use for uncertain experiments; commit only if the spike result is worth preserving, otherwise record findings and discard or isolate the experiment.

Do not commit broken or purely transitional states unless the route explicitly needs an archival spike commit. Avoid broad mixed commits. A good commit has one clear purpose, includes matching tests/docs when needed, and can be reverted without unrelated fallout.

Before committing:

1. Inspect `git status` and `git diff`.
2. Confirm the diff matches the intended workstream and excludes unrelated user changes.
3. Run the route's required validation for the changed surface.
4. Run the review-fix loop below.
5. Record the commit hash, summary, validation, and residual risk in the scratchpad after the commit succeeds, then consolidate durable commit evidence into the route at slice close.

Use concise imperative commit messages. Include a scope when it helps, for example `skift: add status drift detection`.

## Review-Fix Loop

Run this loop before every commit and when closing a slice.

1. Review the diff as a code reviewer, prioritizing correctness, regressions, data loss, security/privacy, public API/UX drift, missing validation, and maintainability.
2. Classify findings as:
   - `must-fix`: correctness, regression, data-loss, security/privacy, unsupported public behavior, or failing validation.
   - `should-fix`: plausible edge case, confusing UX, weak test coverage, or maintainability issue within the active scope.
   - `record/defer`: real but outside the active slice, low-risk polish, or blocked by a user/product decision.
3. Fix all `must-fix` and in-scope `should-fix` findings.
4. Re-run targeted validation after fixes.
5. Review the evidence claim for inflation: the proof must match the claimed evidence level, and the summary must say what is not proven when the validation is lower than the real target.
6. Repeat review and fix until a full review pass finds no `must-fix` issues, no in-scope `should-fix` issues, and no inflated evidence claim.
7. Record deferred findings in the scratchpad and, if durable, the route.

Convergence means one clean review pass after the latest fix. If the same issue class persists after repeated attempts, stop only when a stop rule applies or a user/product decision is genuinely required; otherwise keep narrowing and fixing.

## Route Design

A route is the stable project plan. It should be specific enough to guide hours of work and flexible enough to allow evidence-based pivots.

Before drafting workstreams, classify the route's system profile: `bounded service/API`, `data/algorithm`, `provider/cloud`, `simulator/eval`, `large refactor/migration`, or `mixed`.

If the profile is `data/algorithm`, `provider/cloud`, `simulator/eval`, or `mixed`, read `references/high-risk-route-profiles.md` before writing the route. Use it to add required contracts, sharp-edge guardrails, and evidence labels without copying project-specific cases.

Always include first closure:

- `Whole Goal`: the full project outcome.
- `Whole Goal Checklist`: a scannable outcome-level progress table with `done`, `doing`, `todo`, `blocked`, and `deferred` statuses.
- `First Autonomous Slice`: the first few-hour closure target.
- `Stretch Goals`: optional work after first slice validates.
- `Explicitly Deferred`: work left for later because it is high risk, blocked on external access, or too broad.

The checklist is a status surface, not a rigid low-level implementation script. Each item should name an outcome or externally meaningful capability, the evidence that will prove it, and the next action. Avoid filling it with tiny code-edit steps.

Prefer a first slice that:

- Builds or strengthens the validation harness.
- Exercises a thin vertical path through the system.
- Locks public/API behavior with tests.
- Avoids the riskiest unproven implementation until there is a spike or test matrix.

For high-risk profiles, the first slice should normally be a production-shaped vertical slice plus an evidence ladder, not a broad implementation pass.

## Validation Surface Map

Map validation surfaces separately from implementation tasks:

- unit tests
- integration tests
- contract tests
- SDK/client compatibility tests
- benchmarks/profiles/load tests
- static checks/types/lints
- logs/metrics/audit assertions
- screenshots/visual regression checks
- migration counts or data integrity checks
- failure-path and rollback tests

If validation is weak, make validation-harness creation part of the first autonomous slice.

## External Freshness

If the task depends on an external API, SDK, protocol, model capability, browser behavior, cloud service, law, price, or standard, require a freshness check before implementation.

Record in the route or scratchpad:

- source URL or local reference
- checked date
- version assumptions
- observed behavior if tested
- conflicts with the source spec

When the source spec conflicts with current official docs or actual SDK behavior, do not silently choose. Record the conflict, choose the source of truth for the active slice, and add a stop rule if the choice is product-sensitive.

## Risk Triage

Classify major work areas as:

- `implement now`: clear enough and covered by validation.
- `spike first`: risky or uncertain; run a prototype/test matrix before committing to implementation.
- `defer`: useful but outside the first autonomous slice.
- `ask user`: requires product, business, security, credential, production, or destructive-operation approval.

## Route Template

```markdown
# Route-Driven Work: <name>

## System Profile
- Profile: <bounded service/API | data/algorithm | provider/cloud | simulator/eval | large refactor/migration | mixed>
- Validation consequence: <extra contracts/evidence needed, or none>

## Whole Goal
<Full project outcome, including later phases.>

## Whole Goal Checklist
| Status | ID | Outcome | Evidence | Next Action |
| --- | --- | --- | --- | --- |
| todo | G1 | <outcome or capability> | <command/artifact/result that proves it> | <next concrete action> |

## First Autonomous Slice
<The first few-hour closure target. Include what is in, what is out, and what evidence proves it closed.>

## Active Scratchpad
- Current: none
- Naming: `docs/work-scratchpad-<slug>-<slice-id>.md`
- Rule: one scratchpad per slice. Create it only when execution starts or a new slice begins.

## Success Criteria
- <Metric or acceptance criterion>
- <Correctness/stability criterion>
- <Regression criterion>

## Non-Goals
- <Explicitly excluded work>
- <External systems or risky changes not required for this route>

## Explicitly Deferred
- <High-risk phase or feature deferred from the first slice>
- <External integration or production validation deferred until approval>

## Completed Slices
| Slice | Status | Summary | Evidence | Key Decisions | Follow-Ups |
| --- | --- | --- | --- | --- | --- |
| <slice> | done/deferred/blocked | <summary> | <commands/artifacts> | <decision> | <next work> |

## Durable Findings
- <Stable finding, verified result, or disproven hypothesis from completed work>

## Guardrails
- <Compatibility rule>
- <Data/security/destructive-operation rule>
- <When to ask the user>

## High-Risk Addenda
For `data/algorithm`, `provider/cloud`, `simulator/eval`, or `mixed` profiles, include the required contracts, sharp-edge register, and evidence claim template from `references/high-risk-route-profiles.md`.

## Validation Surface Map
| Surface | Purpose | Command / Method | Required For First Slice |
| --- | --- | --- | --- |
| unit | <what it proves> | `<command>` | yes/no |
| contract | <what it proves> | `<command>` | yes/no |

## Evidence Plan
- Baseline commands:
  - `<command>`
- Validation commands:
  - `<command>`
- Artifacts to collect:
  - `<artifact>`

## Risk Triage
| Area | Classification | Reason | First Action |
| --- | --- | --- | --- |
| <area> | implement now / spike first / defer / ask user | <why> | <action> |

## Workstreams
| ID | Status | Priority | Slice | Workstream | Hypothesis | Validation | Done When | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W1 | todo | P0 | first | <baseline/harness> | <why it matters> | <how to test> | <completion definition> | <risk> |

## Commit Plan
- Cadence: <per validated workstream / per vertical slice / per harness then implementation / spike branch only>
- Commit boundaries:
  - <boundary and validation required before commit>
- Commit standard: each commit is review-clean, validated, logically reversible, and excludes unrelated user changes.
- Pre-commit review-fix loop: required; repeat until no must-fix or in-scope should-fix findings remain.

## Execution Rules
1. Read this route and the source documents.
2. Create a scratchpad for the active slice on execute or when a new slice begins, then set `Active Scratchpad` to its path.
3. Record git status and branch.
4. Establish baseline.
5. Pick the highest-value workstream in the active slice.
6. Implement the smallest reversible change.
7. Validate, compare, document, run review-fix to convergence, and commit if review-clean.
8. When a slice closes, consolidate durable findings into this route, update the Whole Goal Checklist, and mark the scratchpad closed.
9. Before stopping, run a Stop Audit against the Whole Goal Checklist.
10. Unless every non-deferred checklist item is done, a stop rule triggers, or the user explicitly requested only this slice/workstream, continue with the next highest-value unblocked checklist item or workstream and create a fresh scratchpad for it.

## Pivot Rules
- If a hypothesis is disproven, mark it disproven and choose the next best workstream.
- If a new bottleneck or risk appears, add it to the scratchpad with evidence before changing direction.
- If validation is noisy, repeat or narrow the experiment before claiming success.
- If external docs or SDK behavior conflict with the route, record the conflict and decide whether it is a local implementation detail or a stop-rule issue.
- If the first slice expands beyond a few-hour closure, defer stretch work and close the verified slice first.

## Git Discipline
- Inspect `git status` before edits.
- Never overwrite unrelated user changes.
- Use a feature branch for multi-hour work when appropriate.
- Commit by logical phase: baseline, harness, implementation, docs/results.
- Each commit should be explainable and reversible.
- Before each commit, inspect the full diff, run required validation, and run review-fix until findings converge.
- Do not commit while `must-fix` or in-scope `should-fix` findings remain.

## Stop Rules
- Stop and ask if a product/business tradeoff is required.
- Stop and ask before destructive operations, production access, secret handling, or broad rewrites.
- Stop if the Whole Goal is complete and validation passes.
- Stop if the user explicitly requested only a slice/workstream and that scoped target is complete and validated.
- Stop if blocked after reasonable investigation; record attempts and the specific decision needed.
- Do not stop just because W1, the first slice, or the active slice is done while the Whole Goal Checklist still has unblocked `todo` or `doing` items.
```

## Scratchpad Template

Create this only in execute or continue mode. Each scratchpad belongs to exactly one slice.

```markdown
# Work Scratchpad: <name> / <slice-id>

## Slice State
- Status: doing
- Route:
- Scratchpad:
- Current branch:
- Current commit:
- Slice:
- Source workstream or checklist item:
- Last updated:

## Bounds
- One scratchpad per slice.
- Keep only information needed to resume this slice.
- Do not copy the route's Whole Goal Checklist or full Workstreams list.
- Move durable findings/results/decisions into the route when stable.
- Stop appending to this scratchpad when the slice closes.

## Local Tasks
| Task | Status | Evidence Needed | Result |
| --- | --- | --- | --- |

## Current Hypothesis
- <What is being tested or built now>
- Done when: <slice-local closure condition>

## Recent Evidence
| Time | Command / Method | Result | Artifact / Notes |
| --- | --- | --- | --- |

## Temporary Findings
- <Unstable fact, local observation, or thing to verify before moving to route>

## Open Blockers
- <Blocker, attempts, and required user input>

## Commit Plan
- Cadence:
- Next commit boundary:
- Required validation before commit:

## Review-Fix Notes
| Time | Findings | Fixes Applied | Validation After Fix | Converged |
| --- | --- | --- | --- | --- |

## Next Actions
1. <Next concrete action>
2. <Next concrete action>

## Closeout To Route
- Durable findings copied to route.
- Completed slice summary added to route.
- Evidence and artifacts linked from route.
- Deferred or next-slice work updated in route.
- Active Scratchpad set to `none` or the next slice path.
- Whole Goal Checklist updated.
- Scratchpad status set to closed.
```

## Quality Checks

Before finalizing evaluate mode:

- The suitability decision is explicit.
- Unsuitable tasks include actionable reasons.
- Suitable tasks have a route file but no execution scratchpad yet.
- Large suitable tasks have a Whole Goal Checklist, first autonomous slice, stretch goals, and explicit deferrals.
- The route has a system profile and the validation consequence matches that profile.
- Data/algorithm, provider/cloud, simulator/eval, and mixed routes include required contracts, sharp-edge register entries, and an evidence claim template where relevant.
- The Whole Goal Checklist is near the top of the route, uses only `done`, `doing`, `todo`, `blocked`, and `deferred`, and tracks outcome-level progress rather than tiny implementation steps.
- External specs include freshness/version assumptions when relevant.
- Risky areas are marked implement now / spike first / defer / ask user.
- Validation surfaces are mapped independently from implementation steps.
- The first autonomous slice proves boundary shape or validation harness before broad implementation when the route profile has high correctness or integration risk.
- Commit cadence, boundaries, and review-fix requirements are explicit.
- The route document is not a rigid low-level implementation checklist, but it does include a scannable outcome-level status checklist.
- The user is told how to start in one short sentence.

Before finalizing execute or continue mode:

- The active scratchpad exists and reflects current slice state.
- The route remains the source of strategy and durable status; the scratchpad remains the source of temporary slice execution state.
- The scratchpad is bounded to one active slice and does not copy the route's Whole Goal Checklist or full Workstreams list.
- Closed slice findings/results/decisions are consolidated into the route.
- The Whole Goal Checklist reflects the current state after any slice closure.
- If a slice closed, its scratchpad is marked closed before starting another slice.
- The route's Active Scratchpad points to the current slice scratchpad or `none`.
- Claims are backed by repeatable evidence.
- Evidence labels match the actual proof and do not inflate unit, fake, simulator, or local validation into stronger claims.
- Each commit is preceded by a converged review-fix loop, or the reason no commit was made is recorded.
- A closed first/active slice is treated as a checkpoint, not a terminal state, unless the user explicitly scoped the run to that slice.
- A Stop Audit was performed; if any unblocked `todo` or `doing` checklist item remains, execution continues instead of finalizing.
- Stop rules cover user approval, destructive actions, product tradeoffs, and validation failure.
