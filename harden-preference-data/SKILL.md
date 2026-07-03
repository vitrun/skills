---
name: harden-preference-data
description: Design or audit preference-training data so the model cannot satisfy DPO/RLHF/RLAIF or reward-model signals through cheap shortcuts. Use when the task involves preferred/rejected pairs, hard negatives, same-context contrast, utility validation, proxy-vs-native gaps, reward hacking, metric gaming, shortcut learning, post-training collapse, low badcase-mining yield, or data-side frontier search for preference optimization.
---

# Harden Preference Data

Use this skill to make preference data behave like a shortcut-resistant
experiment, not a loose collection of good and bad examples.

## Core Rule

Assume the optimizer will learn the cheapest feature that predicts the label.
Do not trust a pair because the preferred answer is better to a human. Trust it
only when shallow features cannot explain the label better than the intended
behavioral distinction.

A fully reviewed, contract-clean dataset can still teach a shortcut. Passing
manual review row-by-row is necessary, not sufficient: it removes bad examples
but does not change the reward shape. If the optimizer can win by length,
stasis, format, or source, more cleaning will not fix it — only changing what
the contrast carries will.

## Workflow

1. State the intended behavior.
   - Name what the model should do differently after training.
   - Name protected behaviors that must not regress.
   - Separate proxy metrics from downstream/native behavior metrics.

2. Identify likely shortcuts.
   Check whether chosen/rejected labels can be predicted by:
   - length, truncation, or verbosity (the most common shortcut is
     "preferred = shorter, safer, or more static");
   - confidence, refusal, or safety posture;
   - repeated phrases, template openings, or stylistic fingerprints;
   - the voice of the model used to judge labels or to generate preferred
     outputs (a strong generator can imprint style; a weak labeler can
     mislabel);
   - lower action density, less specificity, or safer stasis;
   - answer format, metadata, ordering, or sampling source;
   - reward-model or automated-labeler artifacts rather than semantic quality.

3. Build same-context, multi-negative contrast matched on shallow features.
   Keep the prompt, prefix, state, task, and interaction history fixed and vary
   only the behavior being adjudicated. For each accepted positive, anchor
   several rejected alternatives at that same context, each covering a distinct
   way the model could game the signal: the original failure, an overly short
   answer, an overlong or verbose answer, a fluent but non-useful answer, a
   static or stasis answer, a policy-shaped evasion, and an off-task drift.
   Matching chosen and rejected on length, format, tone, and source is what
   forces the intended behavior — not a shallow feature — to carry the label.
   Anchoring every negative at the same context is what stops the optimizer
   from settling on a prefix-correlated feature instead.

4. Separate exploration from promotion.
   Allow messy but reviewed train-only signal for exploration when it is
   clearly tagged, low-confidence or low-weighted as appropriate, and excluded
   from validation, promotion, or benchmark claims. Keep final evaluation data
   clean, locked, and uncontaminated by fixes derived from its own failures.

5. Validate utility before claiming progress.
   Treat proxy loss, reward accuracy, and pairwise preference accuracy as
   learnability signals only. Run a separate utility or native-behavior check
   for collapse, regressions, output-shape gaming, and task success before
   calling a candidate better.

6. Feed failures back as evidence.
   When a trained candidate discovers a loophole, classify the failure and, if
   it is clean, use that output as a hard negative in the next round under the
   same or closest comparable context.

## Data Design Checklist

Before training, answer these questions:

- What shallow classifier could predict chosen vs rejected without understanding
  the task?
- If every row already passes manual review, what changes about the reward
  shape? (Cleaning removes bad rows; it does not by itself remove a shortcut.)
- Are multiple negatives anchored at the same context as the chosen answer, or
  could a prefix-correlated feature still separate the classes?
- Are chosen and rejected matched on length, format, source, tone, and sampling
  process enough for the intended behavior to carry the label?
- Do positives preserve real task utility, or merely avoid visible badness?
- Do negatives include the model's known failure modes, not just weak baseline
  examples?
- Are hard negatives semantically bad, or only automated-labeler/reward-model
  positive?
- Is the automated labeler failing in both directions — over-firing (false
  positives that drain review yield) and under-firing (real failures that pass
  the gate but fail human/utility review)?
- Has the model used to label badcases and to generate preferred outputs been
  treated as a tunable choice, or assumed fixed? A weak labeler starves the
  pool; a strong generator can imprint its voice.
- Are validation and promotion examples isolated from data generation and
  checkpoint selection?
- Is every non-clean or synthetic source tagged so it cannot be mistaken for
  promotion evidence?

If the answers are weak, change the contrast shape — what the pair carries —
before tuning optimizer parameters. More review or more rows alone will not
remove a shortcut.

## Evaluation Checklist

After training, inspect for:

- improved proxy metrics with downstream/native regression;
- terse, generic, static, evasive, or low-utility outputs;
- overlong, repetitive, or budget-filling outputs;
- protected-task or control-regression failures;
- automated-labeler false negatives that still fail human review, and false
  positives that starved the data pool before training;
- style imitation without behavioral improvement;
- improvements limited to the exact data distribution used for fixes.

Reject or downgrade candidates that improve the proxy by moving into a known
shortcut basin.

## Recommended Output

When reporting an audit or plan, include:

- Intended behavior: what the data is supposed to teach.
- Shortcut risks: shallow features that may predict labels.
- Contrast design: how contexts are matched and what varies.
- Hard-negative map: failure modes covered by rejected examples.
- Data-boundary plan: what is train-only, validation, promotion, or diagnostic.
- Utility validation: checks required before any frontier or quality claim.
- Next action: smallest data or eval change that reduces shortcut surface.

## Boundaries

Do not invent a universal schema for preference data. Adapt the protocol to the
project's actual artifacts, labels, and metrics.

Do not add generic scripts unless the current project has stable input
contracts. For most uses, this skill should produce a checklist, data-design
plan, audit report, or next-experiment queue rather than code.

When the user is running open-ended multi-objective frontier search, use this
skill together with `frontier-search`: `frontier-search` manages candidates and
dominance; this skill hardens the preference signal inside each candidate.
