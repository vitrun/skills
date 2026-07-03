# ML/LLM Frontier Hygiene

Use this reference when a frontier search involves data construction, model
training, prompt optimization, eval scanners, judges, or benchmark metrics that
can be gamed.

## Feedback Loop

Model and prompt frontiers should be managed as a closed loop:

`data or prompt signal -> trainer/eval code contract -> cheap proxy metric -> saved task behavior -> taxonomy/manual review -> attribution -> next axis`

Do not let any single metric become the acceptance authority unless the user
explicitly defined it as the product objective and its gaming risk has been
audited.

## Meaningful Run Boundary

Treat a run as meaningful when it can influence a frontier decision, spend
material GPU/cloud/API budget, train or tune a model, alter a prompt/judge/
scanner used for selection, or change the ranking of candidates.

Cheap local probes, schema checks, one-step finite smokes, and artifact
inspection can run before all gates are complete, but they must be labeled as
probes and cannot support a frontier claim by themselves.

## Hard-Gated Round Lifecycle

For meaningful ML/LLM rounds, use a hard gate at both ends:

1. **Pre-run permission.** Do not launch the run until the pre-run gates pass
   or the scratchpad records an explicit narrow-ablation exception.
2. **Run closeout.** Do not launch the next meaningful run until the current
   run has a closeout artifact with post-run analysis, attribution, and a
   next-run permission decision.

The only exception is an emergency or cleanup run needed to recover artifacts,
stop cost leakage, or reproduce a failed execution path. Mark it as recovery,
not as a new frontier candidate.

## Lesson Operationalization Gate

For ML/LLM frontiers, a lesson from a failed or suspicious run is not considered
implemented when it only appears in a scratchpad, closeout, or final answer.
Before approving the next meaningful run, convert any recurring or causal
lesson into at least one enforceable surface:

- a pre-run permission blocker;
- a data or prompt materialization gate;
- a trainer, eval, judge, scanner, or runtime config check;
- a review checklist item with required row or output evidence;
- a reproducible script or probe;
- a closed-axis rule with explicit reopen conditions.

If the next proposal can repeat the same shortcut without tripping one of those
surfaces, the run is blocked. The correct next action is to write the gate or
change the mechanism, not to run another variant and rediscover the lesson.

## Pre-Run Gates

Before spending meaningful compute or API budget, require:

- a closeout for the previous meaningful run, unless this is the first run on
  the frontier or an artifact-recovery run;
- a mechanism hypothesis, not only a candidate name;
- comparator and protected regression metrics;
- a metric-gaming pre-mortem;
- data or prompt distribution report;
- code review for changed trainer, judge, scanner, materializer, or eval logic;
- one cheap smoke when objective or runtime code changed;
- clear stop rule and next-axis decision boundary.

## Metric Skepticism

Treat these as diagnostics until task-level validation agrees:

- proxy loss, validation loss, pairwise accuracy, or reward-model score;
- scanner-positive count;
- judge preference rate;
- prompt self-eval;
- preferred-side shape audit;
- benchmark subscore without saved examples.

When a metric becomes near-perfect, inspect for a new shortcut before
celebrating.

## Comparability Audit

Run a comparability audit whenever any of these changes:

- scanner or judge rubric;
- prompt or eval template;
- manual quality standard;
- model decoding defaults;
- dataset split or source overlap;
- trainer objective, row order, weighting, masking, or reduction;
- base cache or adapter loading path.

Backscore active incumbents and challengers under the new standard before
making dominance claims.

## Code Review Gate

For trainer/eval/data code changes, review:

- intended semantic change;
- defaults and artifact-recorded effective config;
- row order, sampling, loss reduction, masking, and weighting;
- weighted versus unweighted telemetry;
- finite smoke and probe coverage on the actual runtime path;
- whether the runtime gate still matches the semantic risk.

Do not rely on validation-loss improvement alone for objective-shape changes.

## Data And Reward-Shape Audit

For training-data or prompt-example changes, inspect what the optimizer can
learn cheaply:

- chosen/rejected or good/bad examples separable by length, style, or template;
- weak negatives that do not target the native failure mode;
- teacher-style artifacts;
- over-representation of one source/head/scenario;
- held-out residual leakage;
- examples that are clean but low utility;
- missing control/ordinary-case preservation.

Prefer same-context contrasts and hard negatives that force the intended
behavior to explain the label better than shallow features.

## Post-Run Analysis

Every meaningful candidate should produce:

- aggregate metrics against base and comparator;
- fixed/regressed or win/loss transition table;
- distribution audit, especially length and budget saturation;
- taxonomy of residuals and new regressions;
- saved examples for representative wins, losses, and suspicious metric wins;
- manual or independent review when the candidate is near-frontier.

## Run Closeout Hard Gate

Before any next meaningful run, write a closeout that includes:

- **Artifact identity:** candidate id, code version, data/prompt/judge/scanner
  versions, model/base/cache/adapter identifiers, decoding settings, random
  seeds, and exact commands or launch configs.
- **Comparator frame:** base, incumbent, protected metrics, acceptance floor,
  and whether the result is comparable to earlier candidates.
- **Task behavior evidence:** saved outputs or examples, not just aggregate
  proxy metrics.
- **Transition analysis:** fixed/regressed/same-positive/same-negative,
  win/loss, or equivalent pairwise movement against the comparator.
- **Distribution analysis:** token/length/budget saturation, refusal/empty
  rates, source or slice balance, and other known collapse surfaces.
- **Failure taxonomy:** residual failures, new regressions, suspicious metric
  wins, and any scanner/judge false positives or false negatives discovered.
- **Manual or independent review decision:** whether review was required, what
  was reviewed, verdict counts, and unresolved risks. Near-frontier or
  suspicious metric wins require saved-output review before frontier status.
- **Causal attribution:** name the most likely cause: data/reward shape,
  objective/trainer mechanism, prompt shape, judge/scanner blind spot, model
  capacity, source distribution, runtime artifact issue, or inconclusive.
- **Lesson operationalization:** which findings became blockers, gates,
  checklists, scripts, artifact contracts, or closed-axis rules before the next
  run. If none, explain why no durable lesson was learned.
- **Axis decision:** close, pause, continue, deepen, or pivot the axis, with
  the condition that would reopen a closed axis.
- **Next-run permission:** explicit `allowed` or `blocked`. If allowed, state
  the next run's mechanism delta and falsification condition.

If any required closeout evidence is missing, mark the next meaningful run
`blocked` unless the next run is solely for artifact recovery or reproducing
the missing evidence.

## Next-Run Permission Gate

The next meaningful run must answer the current closeout. It should change at
least one of reward shape, objective class, model capacity, source
distribution, prompt/eval surface, or reviewer/judge/scanner standard in a way
that is tied to the attribution.

Do not approve the next run when:

- the previous run has no closeout;
- proxy metrics improved but saved task behavior regressed and the new run does
  not target the observed regression;
- the same shortcut or collapse mode survived two rounds and the proposed run
  is another scalar sweep or same-shape data/prompt append;
- the run only increases volume without explaining why volume changes the
  reward basin;
- the run depends on a prior lesson that has only been written as narrative and
  has not been operationalized as a blocker, gate, checklist, config check,
  script, artifact contract, or closed-axis rule;
- the pre-run data/prompt audit says labels or wins are likely separable by a
  shallow feature such as length, style, template, source, or judge artifact;
- the run cannot be evaluated under a comparable base/comparator surface.

## Stop And Pivot Rules

Stop deepening an axis when:

- the previous meaningful run has no closeout;
- proxy improves while task behavior regresses;
- the same shortcut survives two rounds without a new mechanism;
- a scalar sweep changes numbers but not failure taxonomy;
- a metric revision makes old results non-comparable;
- data cannot be reviewed at the semantic level required by the task;
- the next run lacks a falsifiable hypothesis.

Pivot by changing reward shape, objective class, model capacity, source
distribution, or eval surface. Do not keep adding similar rows or prompts just
because the last result was "almost" better.
