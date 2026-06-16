# Pattern Extraction

Read for transfer structure, not just for paper summary.

## Core Lens

Extract the structure that generated the result:

> When a task has bottleneck X under constraint Y, use structure or mechanism Z to reframe the problem from A to B, gaining C at the cost of D.

Avoid labels such as "uses contrastive learning" or "is a RAG paper" unless they are backed by a reusable move.

## Paper Reading Pass

1. Write a one-sentence as-is summary: task, bottleneck, method, result.
2. Identify why previous methods fail: missing information, wrong objective, unsuitable representation, hard optimization, high cost, distribution shift, or poor evaluation.
3. Find the key observation the authors exploit.
4. Name the transformation: "from ____ to ____".
5. Abstract away paper-specific nouns into variables.
6. Record transfer conditions and failure conditions.
7. Generate at least one research question from an assumption, tradeoff, or failure mode.

## Problem Pattern

Capture:

- Background tension: the field-level contradiction the paper notices.
- Old assumption challenged: what previous work implicitly assumed.
- Problem reframing: how the authors redefined the task or evaluation.
- Bottleneck: the recurring obstacle this paper makes visible.

Common tensions include performance vs cost, data volume vs label quality, expressiveness vs control, end-to-end learning vs structure prior, scalability vs fine modeling, and local optimization vs global consistency.

## Solution Pattern

Capture:

- Core lever: representation, objective, architecture, data construction, training dynamics, inference procedure, evaluation protocol, retrieval/tool/memory, or decomposition.
- Inductive bias: what structure of the world the method assumes.
- Mechanism: the minimum reusable algorithmic shape.
- Tradeoff: what cost buys the gain.

## Transfer Tests

Before calling something a pattern, test it:

- Can it be restated without original paper-specific names?
- Does it transfer to a distant domain with analogous variables?
- Does it generate a new research question?
- Are its assumptions and failure modes explicit enough to prevent blind reuse?
