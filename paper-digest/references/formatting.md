# Paper Digest Formatting

Use this Markdown heading structure exactly when publishing:

- The date/run title is the only H2: `## YYYY-MM-DD Paper Digest`.
- Each paper title is H3: `### <paper title>`.
- Do not use H2 for paper titles.
- Keep per-paper details as bullets under H3.
- If a nested label is needed, use bold text inside bullets such as `- **Method:** ...`, not another heading.

For each paper, include:

- Title.
- One link only: prefer arXiv when available, otherwise AlphaXiv.
- Authors or institutions when useful.
- One grouped `Problem` bullet with one or two sub-bullets.
- One grouped `Method` bullet with one or two sub-bullets.
- One grouped `Insight/Result` bullet with one or two sub-bullets.

Keep bullets short and concrete. Avoid copying large abstracts verbatim.

Before publishing:

```bash
# Expected: exactly one line, the date/run title.
rg -n '^## ' digest.md

# Expected: one H3 per paper.
rg -n '^### ' digest.md
```

If a runner emits paper titles as `##`, rewrite those paper title headings to `###` before inserting into the document. Do not publish Markdown where `^## ` matches anything other than the date/run title.
