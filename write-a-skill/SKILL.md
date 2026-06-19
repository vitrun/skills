---
name: write-a-skill
description: Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, or build a new skill.
---

# Writing Skills

## Process

1. **Gather requirements** - ask user about:
   - What task/domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

2. **Draft the skill** - create:
   - SKILL.md with concise instructions
   - `references/` files for detailed or branch-specific guidance
   - Utility scripts if deterministic operations needed

3. **Review with user** - present draft and ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Workflow Contract

Before drafting, define the reusable workflow the skill packages:

- **Decomposition** - how the agent breaks the task into steps or branches.
- **Validation rules** - what evidence proves completion, and what claim each check supports.
- **Output format** - the concrete artifact, summary, file, PR, or structured response expected.
- **User preferences** - durable choices about destinations, tone, notifications, approvals, or defaults.
- **Stop rules** - when to ask the user, refuse to proceed, or avoid changing files.

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── references/        # Detailed docs (if needed)
├── examples/          # Usage examples (if needed)
└── scripts/           # Utility scripts (if needed)
    └── helper.js
```

## SKILL.md Template

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files: See `references/<topic>.md`]
```

## Authoring Details

Read `references/authoring-details.md` when drafting or reviewing descriptions, script decisions, file splitting, or checklist tradeoffs.

## Review Checklist

After drafting, verify:

- [ ] Description includes triggers ("Use when...")
- [ ] SKILL.md under 100 lines
- [ ] No time-sensitive info
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] Workflow contract covers decomposition, validation, output, preferences, and stop rules
- [ ] References one level deep
