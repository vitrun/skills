# Reporting and Boundaries

The final report is for a human prompt owner, not for automatic rollout.

## Report Shape

Use this structure:

```md
# Prompt Badcase Advisor Report

## One-line Conclusion

## Input Overview
- Prompt:
- Badcases:
- Taxonomy:

## Summary
- Badcase count:
- Evidence count:
- Main failure heads:
- Most suspected prompt sections:

## Advice Cards
### A001: HEAD -> Section
- Evidence:
- Diagnosis:
- Suggestion:
- Risk:
- Human questions:

## Uncertainty

## Appendix
- Prompt sections
- Evidence details
```

## No-Patch Boundary

Do not produce:
- a final prompt;
- an exact prompt patch;
- a diff;
- a benchmark winner;
- an online rollout recommendation.

Allowed:
- "Look at this section."
- "This wording may reward the failure pattern."
- "Consider reducing/increasing this behavior."
- "Risk: this could change style/quality/product behavior."
- "Human question: decide whether this quality goal is intentional."

## Human Escalation

Escalate when:
- the prompt and badcases do not reveal the real product quality goal;
- the user asks whether a style should be preserved or removed;
- a prompt section is owned by another team or tied to policy/compliance;
- advice would change product semantics, not just wording;
- evidence conflicts with known product goals.
