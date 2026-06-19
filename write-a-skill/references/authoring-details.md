# Skill Authoring Details

## Description Requirements

The description is the only skill text an agent sees before choosing whether to load the full `SKILL.md`. Give the agent enough routing information to decide:

1. What capability this skill provides.
2. When and why to trigger it, including specific keywords, contexts, and file types.

Format:

- Max 1024 chars.
- Write in third person.
- First sentence: what it does.
- Second sentence: `Use when [specific triggers]`.

Good example:

```md
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

Bad example:

```md
Helps with documents.
```

The bad example gives the agent no way to distinguish this from adjacent document skills.

## When to Add Scripts

Add utility scripts when:

- The operation is deterministic, such as validation, formatting, extraction, or setup.
- The same code would be generated repeatedly by agents.
- Error handling needs to be exact and reusable.

Scripts save tokens and improve reliability compared with generated one-off code.

## When to Split Files

Move content out of `SKILL.md` when:

- The hub exceeds 100 lines.
- Content is only needed for a conditional branch.
- Content has distinct domains, schemas, providers, or workflows.
- Advanced features are rarely needed.

Use `references/` for detailed workflows, API notes, checklists, and gotchas; `scripts/` or `bin/` for deterministic logic; `assets/` for reusable templates or schemas; and `examples/` for concrete inputs and outputs.
