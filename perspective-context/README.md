# Perspective Context

Perspective Context is a skill for getting better answers from large, mixed materials. It makes the agent build a focused intermediate representation before it audits, diagnoses, or recommends changes.

The core idea:

```text
raw material -> perspective-specific context -> expert inspection
```

This is not about making prompts prettier. It is about changing the shape of the input so the agent can reason along a clear chain instead of spending most of its effort finding and organizing the relevant facts.

## When To Use It

Use this skill when you have a broad or messy input and want the agent to find problems, evaluate risk, or recommend improvements.

Good fits:

- Audit a codebase for reliability issues.
- Review a PRD for missing states or permissions.
- Check a data pipeline or metric definition.
- Diagnose a recommendation system effect loop.
- Understand an organizational delivery or decision process.

Poor fits:

- A small focused question.
- A known bug with an existing reproduction path.
- A single file that is already easy to inspect.
- A request where you only want a direct edit, not analysis.

## How To Ask

You can name a lens:

```text
Use $perspective-context to extract the request lifecycle for this service, then audit reliability risks.
```

Or state the goal and let the agent choose:

```text
Use $perspective-context to review this PRD. I care about ambiguous states, missing recovery paths, and permission gaps.
```

For recommendation or ML systems:

```text
Use $perspective-context to reshape this design into a sample-to-serving chain, then check for offline/online mismatch and attribution gaps.
```

For data metrics:

```text
Use $perspective-context to build the metric definition chain first, then audit where the dashboard number could drift from product reality.
```

## What The Agent Does

1. Chooses a perspective such as request lifecycle, data lineage, state machine, user journey, permission model, dependency graph, cost structure, or feedback loop.
2. Extracts only the facts relevant to that perspective.
3. Builds an evaluative-neutral intermediate representation.
4. Marks missing critical information instead of inventing it.
5. Audits the representation against the user's goal.
6. Reports concrete findings tied back to stages, states, modules, or missing facts.

## Why This Exists

Directly asking "what is wrong with this large thing?" often produces generic answers because the agent has to perform four tasks at once:

1. Find relevant information.
2. Invent a useful structure.
3. Identify problems.
4. Recommend changes.

Perspective Context separates the first two tasks from the last two. Once the material is reshaped into a checkable chain, the agent can inspect it more like an expert reviewer.

## Output Expectations

For analysis requests, expect a compact `Perspective Context` section followed by findings.

For implementation requests, the agent may keep the intermediate representation as working context and report only the changes, validation, and remaining decisions.

The intermediate representation should be faithful, not flattering. Missing facts should be visible.
