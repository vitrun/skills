---
name: perspective-context
description: Reshape large mixed materials into a focused intermediate representation before analysis. Use when the user asks to audit, diagnose, improve, find problems in, or review complex docs, codebases, PRDs, data systems, product flows, operations, or architecture, and the answer needs a lens such as request flow, data lineage, state, permissions, dependencies, cost, or feedback loop.
---

# Perspective Context

Use this skill to turn messy source material into a lens-specific object that can be inspected before giving advice. The core move is: choose a perspective, extract only the relevant facts, organize them into an intermediate representation, then analyze that representation.

Do not treat this as prompt polishing. The goal is to change the input shape.

## Resource Map

- Read [references/lens-catalog.md](references/lens-catalog.md) when choosing or adapting a perspective.
- Read [references/examples.md](references/examples.md) when drafting an intermediate representation for a common domain.

## When To Use

Use this skill when all are true:

- The source material is broad, mixed, or cross-cutting.
- The user wants diagnosis, audit, improvement, prioritization, or problem discovery.
- A chain, state, dependency, ownership, or causality view would make the answer more precise.

Do not use this skill for:

- Small, already-focused questions.
- Single-file explanations where the structure is obvious.
- Direct bug fixes where the reproduction and failing path are already known.
- User-provided intermediate representations that are already adequate.

## Workflow

1. **Pick the perspective**
   - Use the user's named perspective if present.
   - If none is named, pick the smallest lens that matches the goal.
   - Default mappings:
     - Code reliability: request lifecycle or error path.
     - Architecture review: dependency graph or module responsibility map.
     - Product/PRD review: user journey, state machine, or permission matrix.
     - Data/metrics review: lineage, metric definition chain, or feedback loop.
     - Recommendation/system-effect review: effect loop or sample-to-serving chain.

2. **Extract facts**
   - Work from the provided material or the real files the user authorized.
   - Keep only facts relevant to the chosen lens.
   - Preserve source names, file paths, identifiers, metrics, APIs, configs, and explicit constraints.
   - Mark missing critical information as `Not specified` or `Not found`; do not invent it.

3. **Build the intermediate representation**
   - Organize by ordered stages, causal links, state transitions, dependencies, or ownership boundaries.
   - Keep it evaluative-neutral: no recommendations, no premature judgments.
   - Make it independently readable enough that another agent could inspect it without re-reading the full raw material.

4. **Analyze against the user's goal**
   - Check for breaks, hidden assumptions, inconsistent terminology, missing transitions, unowned dependencies, delayed feedback, lost information, local optimizations that hurt the global goal, and unverifiable claims.
   - Tie every finding back to a stage, edge, state, module, or missing fact in the intermediate representation.

5. **Choose output shape**
   - If the user asks for analysis only, show a compact `Perspective Context` section before findings.
   - If the intermediate representation is large, summarize it and attach the full version only when useful.
   - If the user asks for implementation or patching, use the representation as working context and report only the changes, validation, and remaining decisions.

## Quality Bar

- The perspective should reduce search work for the analysis, not add ceremonial structure.
- The intermediate representation should let the agent move from reading comprehension to inspection.
- Findings must be specific enough to verify against the representation or source material.
- If two lenses are plausible and would lead to materially different audits, state the chosen lens and why.
