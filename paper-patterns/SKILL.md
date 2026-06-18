---
name: paper-patterns
description: Extract reusable research patterns from papers and maintain an OKF-style markdown library of Paper, Pattern, Bottleneck, Tradeoff, Assumption, and Research Question concepts. Use when the user asks to 提炼 paper pattern, turn papers into transferable research patterns, build/update a Research Pattern OKF or Obsidian pattern vault, or generate pattern-library notes from papers.
---

# Paper Patterns

Turn research papers into reusable pattern concepts: problem framings, solution levers, bottlenecks, assumptions, tradeoffs, transfer cases, and research questions. Treat papers as evidence; treat patterns as the durable asset.

## Resource Map

- Read [references/pattern-extraction.md](references/pattern-extraction.md) before extracting patterns from a paper.
- Read [references/okf-layout.md](references/okf-layout.md) before creating or updating an OKF-style markdown bundle.
- Use [assets/paper-template.md](assets/paper-template.md) for Paper concepts.
- Use [assets/pattern-template.md](assets/pattern-template.md) for Pattern concepts.
- Use [assets/bottleneck-template.md](assets/bottleneck-template.md) for Bottleneck concepts.
- Use [assets/assumption-template.md](assets/assumption-template.md) for Assumption concepts.
- Use [assets/tradeoff-template.md](assets/tradeoff-template.md) for Tradeoff concepts.
- Use [assets/question-template.md](assets/question-template.md) for Research Question concepts.
- Use [scripts/validate-research-okf.py](scripts/validate-research-okf.py) to check concept frontmatter and local markdown links.

## Boundaries

- Use `paper-reader` for a normal explanation or deep reading of one arXiv/AlphaXiv paper.
- Use `paper-digest` for recent-paper fetching, curation, publishing, notification, and seen-state updates.
- Use this skill when the user wants durable pattern-library objects or transfer-oriented research synthesis.

## Workflow

1. **Collect source material**
   - Use supplied notes, PDFs, arXiv IDs, AlphaXiv reports, or existing vault notes.
   - For an arXiv ID with no source text, fetch `https://alphaxiv.org/overview/{id}.md`; fall back to `https://alphaxiv.org/abs/{id}.md`.

2. **Extract the transfer structure**
   - Capture the paper's background tension, challenged old assumption, problem reframing, core lever, inductive bias, tradeoffs, and failure conditions.
   - Name the transferable move as `from X to Y`, not as a surface technique label.

3. **Decide concept changes**
   - Create or update one Paper concept for the source.
   - Create or update one to three Pattern concepts.
   - Link or create Bottleneck and Research Question concepts when they clarify transfer boundaries.
   - Avoid premature ontology growth; keep assumptions/tradeoffs inline until they recur enough to deserve separate files.

4. **Write OKF-style markdown**
   - Use YAML frontmatter with at least `type`, `title`, `description`, `tags`, and `timestamp`.
   - Use stable relative links between concepts.
   - Update nearby `index.md` and `log.md` when present.

5. **Validate and report**
   - Run the validation script for any bundle you touched.
   - Report created/updated concept files, validation result, and any unresolved links or synthesis follow-up.

## Quality Bar

- A good Pattern can be restated without the original paper's proper nouns.
- A good Pattern names when it transfers and when it fails.
- A good Paper note points to patterns; it is not just a summary.
- A good Question emerges from a pattern's assumption, tradeoff, or failure mode.
