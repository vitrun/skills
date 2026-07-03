# Output Contracts

The validator checks these contracts. Prefer stable IDs, explicit uncertainty,
and cross-file references over prose-only conclusions.

## Confidence Values

Use `low`, `medium`, or `high`.

## Badcase Attributor Files

### `task_understanding.json`

Required fields:
- `task_summary`: string
- `target_output`: object
- `quality_goals`: list
- `hard_constraints`: list
- `confidence`: confidence value
- `uncertainties`: list

### `badcase_schema.json`

Required fields:
- `record_format`: string
- `conversation_fields`: object
- `human_labels`: list
- `score_fields`: list
- `metadata_fields`: list
- `confidence`: confidence value
- `warnings`: list

### `failure_taxonomy.json`

Required fields:
- `heads`: list of objects with `id`, `label`, `severity`, `definition`,
  `source`, and optional `evidence_patterns`
- `uncertainties`: list

### `badcase_evidence.jsonl`

Each row requires:
- `evidence_id`: stable ID unique within the run
- `case_id`: standard badcase record ID
- `head`: failure head ID
- `severity`: severity string
- `quote`: short verbatim or paraphrased snippet from the badcase
- `why`: why the snippet matters
- `confidence`: confidence value

### `badcase_attributions.jsonl`

Each row requires:
- `case_id`
- `heads`: list of objects with `head`, `severity`, `confidence`, `reason`,
  and `evidence_ids`
- `uncertainties`: list

`evidence_ids` must point to rows in `badcase_evidence.jsonl`.

## Prompt Advisor Files

### `prompt_schema.json`

Required fields:
- `sections`: list of prompt sections
- `uncertainties`: list

Each section requires:
- `section_id`
- `name`
- `line_start`
- `line_end`
- `summary`
- `text_hash`
- `detection_method`
- `confidence`

### `prompt_section_attributions.jsonl`

Each row requires:
- `case_id`
- `head`
- `evidence_ids`
- `suspected_sections`: list

Each suspected section requires:
- `section`: section ID or section name from `prompt_schema.json`
- `confidence`
- `reason`

### `advice.json`

Required fields:
- `schema`: use `prompt_badcase_advice_v1`
- `run_id`
- `summary`
- `advice_cards`

Each advice card requires:
- `advice_id`
- `head`
- `priority`
- `suspected_sections`
- `evidence_ids`
- `diagnosis`
- `suggestion`
- `risk`
- `human_questions`
- `confidence`
- `uncertainties`
- `not_a_patch`: must be `true`

Forbidden fields anywhere in an advice card:
- `patch`
- `diff`
- `final_prompt`
- `candidate_prompt`
- `rewritten_prompt`
- `direct_patch`
- `prompt_patch`

The suggestion may describe a direction, but it must not be a directly
applicable prompt replacement.
