---
name: prompt-badcase-advisor
description: Analyze model badcases against a prompt, extract evidence-backed failure attribution, and produce prompt advice without auto-editing or selecting a final prompt. Use when the user asks to diagnose prompt badcases, badcase 归因, prompt 问题定位, prompt advice from failed outputs, RPB details.jsonl review, or to turn badcase files/logs/transcripts into a human-reviewable prompt improvement report.
---

# Prompt Badcase Advisor

Use this skill to turn a pile of failed model outputs into a reviewable prompt
diagnosis. The skill does not optimize prompts automatically; it prepares
evidence, asks Codex to reason over the evidence, validates the resulting JSON
contracts, and renders a human report.

## Default Workflow

1. Prepare the run directory:
   ```bash
   python3 prompt-badcase-advisor/scripts/prompt_badcase_advisor.py prepare \
     --prompt prompt.md \
     --badcases badcases/
   ```
   This writes inventory, normalized badcase records, prompt section candidates,
   rule evidence candidates, assumptions, and agent request files.
2. Read `references/workflow.md` and fill the requested agent outputs in order:
   Badcase Attributor first, then Prompt Advisor.
3. Validate the completed run:
   ```bash
   python3 prompt-badcase-advisor/scripts/prompt_badcase_advisor.py validate \
     --run-dir results/prompt_badcase_advisor/<run_id>
   ```
4. Render the final report:
   ```bash
   python3 prompt-badcase-advisor/scripts/prompt_badcase_advisor.py render \
     --run-dir results/prompt_badcase_advisor/<run_id>
   ```

## Inputs

- Required: a prompt file and a badcase file or directory.
- Optional: `--context` for product goals or immutable prompt areas.
- Optional: `--taxonomy` for user-supplied failure heads; otherwise use
  `assets/default_taxonomy.yaml` as the baseline.
- Optional: `--adapter`; default to auto-detection.

Supported badcase inputs include RPB `details.jsonl`, OpenAI `messages` JSON,
generic JSONL, CSV, Markdown or text transcripts, and plain text snippets. Read
`references/input-adapters.md` before handling unusual formats.

## Operating Rules

- Keep the two stages separate: Badcase Attributor says what went wrong;
  Prompt Advisor says which prompt sections might be related.
- Preserve uncertainty. Do not turn inferred task goals, field meanings,
  prompt boundaries, or taxonomy heads into user-declared facts.
- Every attribution and advice card must cite evidence. Every prompt advice item
  must cite a prompt section.
- Do not output a direct prompt patch, final prompt, benchmark winner, or online
  rollout recommendation.
- Stop and ask when the user expects business/product quality goals, immutable
  prompt areas, or rollout policy that the prompt and badcases do not reveal.

## References

- `references/workflow.md`: stage order and agent responsibilities.
- `references/output-contracts.md`: required files and validation rules.
- `references/input-adapters.md`: input parsing and fallback behavior.
- `references/reporting-and-boundaries.md`: report shape and no-patch boundary.
- `references/rpb-adapter.md`: optional RPB mapping and lessons from existing
  RPB tooling.

## Output Shape

Report completion with the run directory, validation status, top failure heads,
top suspected sections, and any human questions that block confident prompt
changes.
