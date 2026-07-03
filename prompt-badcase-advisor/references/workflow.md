# Prompt Badcase Advisor Workflow

Use this workflow after `scripts/prompt_badcase_advisor.py prepare` creates a
run directory. The scripts prepare deterministic artifacts; Codex performs the
reasoning stages and writes the JSON files that `validate` checks.

## Run Layout

```text
run_dir/
├── run_manifest.json
├── assumptions.md
├── badcase_analysis/
│   ├── input_inventory.json
│   ├── badcase_records.jsonl
│   ├── badcase_samples.jsonl
│   ├── rule_evidence_candidates.jsonl
│   └── agent_request_badcase_attributor.md
└── prompt_advice/
    ├── prompt_section_candidates.json
    └── agent_request_prompt_advisor.md
```

## Stage 1: Badcase Attributor

Question: what is wrong with these badcases?

Inputs:
- `run_manifest.json`
- `assumptions.md`
- prompt file named in the manifest
- optional context file named in the manifest
- `badcase_analysis/input_inventory.json`
- `badcase_analysis/badcase_records.jsonl`
- `badcase_analysis/badcase_samples.jsonl`
- `badcase_analysis/rule_evidence_candidates.jsonl`
- optional taxonomy file, otherwise `assets/default_taxonomy.yaml`

Write these outputs under `badcase_analysis/`:
- `task_understanding.json`
- `badcase_schema.json`
- `failure_taxonomy.json`
- `badcase_evidence.jsonl`
- `badcase_attributions.jsonl`
- `badcase_report.md`

Rules:
- Explain task goals as inferred from prompt/context, not as user-declared fact.
- Infer field meanings from samples, but preserve uncertain mappings.
- Use rule evidence as recall candidates; do not accept every rule hit blindly.
- Keep this stage free of prompt edit advice.
- Each evidence row needs a stable `evidence_id`, `quote`, `why`, and
  `confidence`.
- Each badcase attribution needs evidence references and an uncertainty list.

## Stage 2: Prompt Advisor

Question: which prompt sections might be related, and what should a human
review?

Inputs:
- all Stage 1 outputs
- `prompt_advice/prompt_section_candidates.json`
- prompt file and optional context from the manifest

Write these outputs under `prompt_advice/`:
- `prompt_schema.json`
- `prompt_section_attributions.jsonl`
- `advice.json`
- `report.md` after running the render script

Rules:
- Use prompt section candidates as deterministic boundaries, but adjust the
  final `prompt_schema.json` if semantic grouping is clearer.
- Attribute to prompt sections as suspected contributors, not certain causes.
- Every prompt section attribution must cite evidence and include confidence.
- Every advice card must include diagnosis, suggestion, risk, human questions,
  confidence, uncertainty, evidence references, suspected sections, and
  `not_a_patch: true`.
- Never write a candidate final prompt or patch.

## Recommended Command Flow

```bash
python3 prompt-badcase-advisor/scripts/prompt_badcase_advisor.py prepare \
  --prompt prompt.md \
  --badcases badcases/

# Fill the requested JSON/JSONL/Markdown outputs with Codex reasoning.

python3 prompt-badcase-advisor/scripts/prompt_badcase_advisor.py validate \
  --run-dir results/prompt_badcase_advisor/<run_id>

python3 prompt-badcase-advisor/scripts/prompt_badcase_advisor.py render \
  --run-dir results/prompt_badcase_advisor/<run_id>
```
