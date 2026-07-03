---
name: frontier-search
description: Search experiment spaces for better multi-objective Pareto frontiers. Use when the user asks for SOTA exploration, Pareto frontier improvement, experiment-axis search, ablations, benchmark-driven discovery, or deciding which technical route is best. Do not use for route-clear execution work; use route-driven-work after the frontier direction is chosen.
---

# Frontier Search

Use this skill when the objective is stable but the best route is unknown. Turn open exploration into a managed search over experiment axes, candidates, evidence, and stop rules.

This skill may borrow the memory discipline of `route-driven-work`, but the durable object is a frontier state, not a fixed route. Use `deli-autoresearch` only when the user explicitly wants unattended orchestration, watchdogs, heartbeat checks, or the Deli AutoResearch protocol.

For ML/LLM, data, prompt, judge, scanner, or benchmark frontiers where metrics can be gamed, also read `references/ml-llm-frontier-hygiene.md` before planning or accepting a candidate.
Treat that reference as a hard-gate protocol for meaningful ML/LLM training,
prompt, judge, scanner, or benchmark runs: do not start the next run until the
previous run has a recorded closeout and the next run is explicitly permitted.

## Lesson Operationalization

A frontier lesson is not durable until it changes the search machinery. Treat a
recurring insight, failure attribution, or review finding as unimplemented until
it becomes at least one of:

- a pre-run permission blocker;
- a stop rule or closed-axis rule with a narrow reopen condition;
- a provider, prompt, or materialization gate;
- a trainer, eval, judge, scanner, or review checklist requirement;
- a reproducible script, probe, or artifact contract.

Do not approve a next experiment merely because the lesson is mentioned in a
scratchpad or closeout. If a later candidate can bypass the lesson without
tripping a gate, the frontier state has not learned it yet.

## Boundary

Use `frontier-search` for:

- SOTA, benchmark, or capability exploration.
- Searching a design/model/prompt/system space for a better Pareto frontier.
- Comparing multi-objective tradeoffs such as quality, latency, cost, stability, complexity, safety, or data requirements.
- Planning ablations and experimental axes before committing to an implementation route.

Use `route-driven-work` instead when the route is already clear enough to execute as workstreams with validation. If a frontier round selects a candidate for implementation, hand that candidate to `route-driven-work` as a route or first slice.

## State Model

Use file-backed memory for any multi-round frontier search:

- `frontier-state-<slug>.md`: durable frontier memory. Store the objective vector, constraints, metric semantics, baseline, axis matrix, candidate ledger, current frontier, dominated/rejected candidates, durable decisions, stop rules, and next experiment queue.
- `frontier-scratchpad-<slug>-<round-id>.md`: temporary working memory for one experiment round. Store the local hypothesis, axis choices, commands/probes, raw observations, blockers, review notes, and closeout checklist.

At round close, consolidate durable results into the frontier state, mark the scratchpad closed, update the current frontier and next queue, then start a fresh scratchpad only if another round begins.

## Workflow

1. Frame the objective vector.
   - Name each metric, direction, hard floor, and protected regression metric.
   - Record budget limits: time, money, compute, data, API calls, or risk.
   - Define what counts as a candidate being comparable to the baseline.
2. Establish the baseline and incumbent.
   - Capture current metrics, commands, datasets, prompts, versions, and reproducibility notes.
   - If no trustworthy baseline exists, make baseline construction the first round.
3. Build the axis matrix.
   - List each axis, candidate values, expected effect, cost, risk, interaction risk, and evidence needed.
   - Prefer broad structural axes before deep tuning of one parameter.
4. Choose the next experiment round.
   - Pick a small candidate set that maximizes expected frontier movement per unit cost.
   - Include at least one falsification or negative-control check when metric gaming is plausible.
   - For ML/LLM frontiers, record the metric-gaming pre-mortem, data or prompt reward-shape audit, and any trainer/eval code-review gate before compute spend.
   - For ML/LLM frontiers, stop before selecting another meaningful run if the previous run lacks the closeout required by `references/ml-llm-frontier-hygiene.md`.
5. Run and record evidence.
   - Keep commands, configs, seeds, data slices, versions, and result artifacts sufficient for repeatability.
   - Label evidence fidelity: toy, offline benchmark, simulator, live-provider, shadow, or canary.
6. Update the frontier.
   - A candidate dominates another only when it is no worse on protected metrics and better on at least one target metric under the stated constraints.
   - If candidates trade off, keep both on the frontier and name the decision boundary.
   - Move failed or inferior candidates to dominated/rejected with evidence and reason.
   - If metric definitions, judges, scanners, prompts, eval templates, trainer mechanics, or manual review rules changed, run a comparability audit before reusing old dominance claims.
   - Convert new durable lessons into an operational rule before treating the round as closed: blocker, gate, checklist, script, artifact contract, or closed-axis entry.
7. Decide the next action.
   - Continue broad search, deepen an axis, run ablations, select a route for implementation, or stop.
   - For ML/LLM frontiers, record whether the next run is allowed or blocked, and why.
   - If the next move relies on a prior lesson, verify that the corresponding gate or rule exists; otherwise create it before approving the run.

## Output Shape

When planning or reporting, produce:

- `Frontier Objective`: metrics, constraints, budget, and baseline.
- `Axis Matrix`: axes, candidate values, expected effects, costs, and risks.
- `Candidate Ledger`: hypothesis, axis combo, evidence, metrics, status, and dominance result.
- `Current Frontier`: non-dominated candidates and the tradeoff each represents.
- `Next Experiment Queue`: ordered rounds with stop conditions.

## Stop Rules

Stop or ask the user when:

- The next move is a product/business tradeoff between frontier candidates.
- Metrics are noisy, gamed, or not comparable enough to support dominance claims.
- Budget, credentials, data access, safety, or production exposure requires approval.
- The frontier has not improved after the configured round or budget cap.
- A candidate is ready to become route-driven implementation work.
- A near-frontier ML/LLM candidate has not yet had saved-output, taxonomy, and manual or independent review sufficient to rule out metric gaming.

Never claim SOTA or production effect from lower-fidelity evidence. State exactly what the evidence proves, what it does not prove, and what validation would raise confidence.
