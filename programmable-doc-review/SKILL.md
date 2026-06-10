---
name: programmable-doc-review
description: Audit and tighten technical design docs until they are implementation-ready for coding agents. Use when a user asks whether a spec, architecture doc, API contract, data contract, or implementation plan is programmable, "crystal clear", ready for coding, or needs human escalation decisions.
---

# Programmable Doc Review

Use this skill to turn technical docs into contracts that independent coding agents can implement consistently. The skill does not replace human judgment; it concentrates human judgment into the few decisions that create product, data, infrastructure, or ownership commitments.

The north star is not "the document sounds complete"; it is "two independent implementers, given the same inputs, would build the same observable behavior, data shapes, state transitions, and acceptance checks."

## Operating Rules

- Start from the current files, sibling docs, IDL, schemas, code paths, logs, or user-provided source of truth. Re-read before patching.
- If the user sets a source boundary, honor it literally. For docs-only review, do not inspect code unless the user reopens that boundary.
- Never invent enum values, thresholds, IDs, RPCs, event names, table fields, SLAs, retention windows, or owner commitments.
- Prefer the smallest viable production contract. Remove vague optionality unless it is intentionally part of the contract and has an owner.
- Final doc text should state settled conclusions. Do not preserve meeting traces, tradeoff discussion, or "we considered" history unless explicitly requested.
- Treat sibling docs, schemas, examples, and diagrams as possible competing sources of truth until the doc declares which one is authoritative.
- When a paragraph uses an action verb such as merge, dedupe, fallback, refill, retry, patch, publish, relax, demote, reconcile, score, normalize, or rebuild, check whether the mechanics are closed enough to code.

## Programmable-Ready Rubric

A doc is programmable when a fresh coding agent can derive the same implementation plan and acceptance result from it:

- Scope, non-goals, deployables/modules, and ownership boundaries are explicit.
- APIs, fields, events, tables, config keys, versions, and external dependencies point to a source of truth or are defined in the doc.
- Read/write side effects, idempotency keys, ordering, consistency, and retry/DLQ behavior are specified where relevant.
- Error semantics, partial/degraded behavior, timeout behavior, and blocking vs non-blocking dependencies are settled.
- Storage keys, retention, versioning, migration/backfill, publish/rollback, and cleanup ownership are defined where relevant.
- Cross-doc terminology is consistent; no stale names survive in sibling docs.
- Each overlapping concept has one declared source of truth. Non-authoritative examples are labeled as examples or removed.
- Algorithms and procedures specify input set, ordering, tie-breakers, mutation/replacement behavior, termination, and whether the process iterates.
- Numeric, enum, boolean, date/time, and transformed fields define value domain, normalization or conversion rule, missing/default semantics, and validation failures.
- Data-plane contracts specify where payload bodies live, how readers locate them, wire/storage format, schema/version binding, and behavior on missing or incompatible data.
- Derived state specifies source facts, watermark, dedupe key, aggregation/update rule, version generation, replay/rebuild path, and idempotency.
- Determinism-critical fields specify canonical ordering, timezone, checksum/hash algorithm, serialization format, and stable tie-breakers.
- Ready checks and validation evidence are concrete enough for implementation start.
- Open questions are few, named, and routed to the owner who can decide them.

## Workflow

1. Identify the target artifact and source hierarchy.
   - List the docs/files/contracts being reviewed.
   - Note whether the user asked for review-only, patching, docs-only analysis, or code-backed analysis.
   - Build a quick source hierarchy: authoritative contract, supporting explanation, illustrative examples, obsolete or replaced sections.
2. Audit for implementation ambiguity.
   - Scan for words like optional, TBD, later, maybe, should support, can provide, depends, reasonable, and not sure.
   - Compare sibling docs for inconsistent field names, ownership, lifecycle, source of truth, or ready conditions.
   - Check whether every consumer-facing statement can be encoded, tested, or monitored.
   - Run a divergence audit: ask where two reasonable implementers could produce different output from the same input.
   - Check procedure closure: for every nontrivial process, identify input collection, output collection, stable ordering, tie-breakers, replacement/mutation rules, retry/relaxation rules, and stop condition.
   - Check data-plane closure: for every referenced artifact, snapshot, payload, state, or generated body, identify its storage location or URI, schema/wire format, reader path, version compatibility, and missing-data behavior.
   - Check transformation closure: for every score, enum, timestamp, key, checksum, hash, derived field, or normalized value, identify its exact formula, value domain, default/missing behavior, and validation failure mode.
   - Check derived-state closure: for every maintained state, identify source facts, watermark, dedupe key, aggregation/update rule, version generation, replay/rebuild path, and idempotency boundary.
3. Classify each gap.
   - `fill`: The agent can patch directly from existing source of truth or a low-risk implementation default.
   - `recommend`: The agent should propose one default because best practice/MVP constraints strongly favor it, but the user may still want to approve.
   - `escalate`: A human must decide because the choice creates or changes product semantics, cross-team ownership, data contracts, external SLAs, cost/compliance posture, or architecture direction.
   - Prioritize by divergence risk first: issues that change observable output, stored data, derived inputs, state transitions, or recovery behavior outrank wording polish.
4. Reduce human load.
   - Do not ask broad "what do you want?" questions.
   - For each escalation, give one recommended option, the reason, and the concrete consequence of choosing differently.
   - Batch related questions; avoid more than three at a time unless the user asks for a full decision log.
5. Patch only after the action mode is clear.
   - If the user asked to patch, apply `fill` changes and clearly separate any remaining `recommend` or `escalate` items.
   - If the user asked to confirm first, stop at the review or proposed contract and wait.

## Decision Boundary

Agent may decide when:

- Existing docs, IDL, schemas, code, or previous user-approved principles uniquely determine the answer.
- The choice is an internal implementation default that does not change user-visible behavior, external contracts, team ownership, or long-term data meaning.
- MVP/best-practice constraints clearly select the smaller reversible option.
- The result can be validated locally by grep, schema checks, tests, or cross-doc consistency review.

Escalate to a human when:

- The decision defines business meaning, metric normalization, attribution, selection/scoring policy, privacy/compliance scope, or product behavior.
- The decision assigns ownership across teams or changes who must produce, store, operate, or certify a contract.
- Multiple plausible designs would create different future architectures or migration paths.
- A source of truth is missing and writing a concrete value would fabricate a contract.
- The user explicitly asks for approval before edits.

## Output Shape

For review-only work, report:

```md
## Readiness
Ready | Ready except N decisions | Not ready

## Agent-fill Items
- ...

## Divergence Risks
- Same input could produce different implementations because ...

## Two-Truth Conflicts
- ...

## Procedure Closure Gaps
- ...

## Data/State Contract Gaps
- ...

## Determinism Gaps
- ...

## Recommended Defaults
- Decision: ...
  Default: ...
  Why: ...

## Human Decisions
- Question: ...
  Recommended answer: ...
  Consequence: ...
```

For patching work, write final contract text only, then verify with targeted grep/diff checks. The final response should name changed files, summarize remaining human decisions, and mention validation performed.
