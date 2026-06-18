---
name: paper-reader
description: Read, explain, and critique a single research paper, using AlphaXiv's machine-readable overview as the default source for arXiv papers. Use when the user shares one paper, arXiv/AlphaXiv URL, or paper ID and asks for summary, explanation, deep reading, assumptions, reproduction, counterexamples, or follow-up ideas. Do not use for recurring paper digests or maintaining a paper-pattern knowledge library.
---

# Paper Reader

Read one paper carefully, then answer the user's question from the paper and clearly marked supporting context. For arXiv papers, use AlphaXiv's structured markdown endpoints before falling back to raw PDF-style reading.

## When to Use

- User shares an arxiv URL (e.g. `arxiv.org/abs/2401.12345`)
- User mentions a paper ID (e.g. `2401.12345`)
- User asks you to explain, summarize, critique, reproduce, or analyze a research paper
- User asks for PaperForge-style deep reading, author-idea reconstruction, weakest assumptions, counterexamples, or follow-up ideas
- User shares an alphaxiv URL (e.g. `alphaxiv.org/overview/2401.12345`)

If the user asks to extract reusable research patterns, update an OKF-style pattern library, or create linked pattern/bottleneck/question notes, use `paper-patterns` instead.

## Workflow

### Step 1: Extract the paper ID

Parse the paper ID from whatever the user provides:

| Input                                      | Paper ID       |
| ------------------------------------------ | -------------- |
| `https://arxiv.org/abs/2401.12345`         | `2401.12345`   |
| `https://arxiv.org/pdf/2401.12345`         | `2401.12345`   |
| `https://alphaxiv.org/overview/2401.12345` | `2401.12345`   |
| `2401.12345v2`                             | `2401.12345v2` |
| `2401.12345`                               | `2401.12345`   |

### Step 2: Fetch the machine-readable report

```bash
curl -s "https://alphaxiv.org/overview/{PAPER_ID}.md"
```

This returns the intermediate machine-readable report — a structured, detailed analysis of the paper optimized for LLM consumption. One call, plain markdown, no JSON parsing.

If this returns 404, the report hasn't been generated for this paper yet.

### Step 3: If you need more detail, fetch the full paper text

If the report doesn't contain the specific information the user is asking about (e.g. a particular equation, table, or section), fetch the full paper text:

```bash
curl -s "https://alphaxiv.org/abs/{PAPER_ID}.md"
```

This returns the full extracted text of the paper as markdown. Only use this as a fallback — the report is usually sufficient.

If this returns 404, the full text hasn't been processed yet. As a last resort, direct the user to the PDF at `https://arxiv.org/pdf/{PAPER_ID}`.

## Error Handling

- **404 on Step 2**: Report not generated for this paper.
- **404 on Step 3**: Full text not yet extracted for this paper.

## Deep Reading Mode

When the user asks for a full reading rather than a narrow answer, cover the paper in this order:

1. Research question, background, and why the problem matters.
2. Prior attempts and why they are insufficient.
3. Reconstructed author reasoning before the method: use only prior work, failure modes, observations, and plausible inspiration; do not use the paper's final contribution as a premise.
4. Core intuition in plain language.
5. Concrete method and one end-to-end example: input, processing, output.
6. Math or theory, with minimal background and intuition if present.
7. Experiments as question -> experiment -> answer.
8. Takeaways.
9. Weakest assumption.
10. One-week minimum reproduction target.
11. Counterexample or attack design.
12. A non-incremental follow-up idea grounded in limitations and real needs.

## Source Discipline

Separate four classes of claims:

- Paper claims: what the paper explicitly says.
- Prior literature: what related work establishes.
- Evidence-based inference: your reasoning from paper evidence or experiments.
- Uncertain guess: plausible but not established.

Do not present reconstructed author reasoning, counterexamples, or follow-up ideas as facts from the paper.

## Notes

- No authentication required — these are public endpoints.
