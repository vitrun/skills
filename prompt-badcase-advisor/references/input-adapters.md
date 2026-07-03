# Input Adapters

The prepare script tries to produce useful records without requiring upfront
configuration. Every record must preserve parse confidence and warnings so later
analysis can avoid overclaiming.

## Standard Badcase Record

```json
{
  "case_id": "source|0",
  "source": "openai_messages",
  "source_path": "badcases/case.json",
  "conversation": [
    {"turn": 0, "user": "...", "assistant": "..."}
  ],
  "scores": {},
  "labels": {},
  "parse_confidence": "medium",
  "parse_warnings": [],
  "metadata": {}
}
```

## Supported Inputs

### RPB `details.jsonl`

Detect when JSONL rows include `conversation` plus `scenario_id` or `dim_scores`.
Map each row to one badcase record. Preserve `scenario_id`, `run_id`, prompt
version fields, dimensions, and scores in metadata/scores.

### OpenAI Messages JSON or JSONL

Detect objects with `messages` containing `role` and `content`. Pair user and
assistant turns in order. Preserve system messages in metadata.

### Generic JSONL or JSON

For rows with common fields such as `input`/`output`, `prompt`/`response`,
`expected`/`actual`, `user`/`assistant`, or `question`/`answer`, create a
single-turn record. Treat `label`, `review_label`, `verdict`, and `annotation`
as human labels. Treat `score`, `overall`, `dim_scores`, and `*_score` as
scores.

### CSV

Use the same field-name heuristics as generic JSON. Include the original row
number in metadata.

### Markdown or Text Transcript

Split turns when lines start with labels such as `User:`, `Assistant:`,
`用户：`, `助手：`, `Human:`, or `AI:`. If no speaker labels exist, treat the
whole file as one assistant failure snippet with low parse confidence.

## Fallback Rules

- Never discard a file solely because the format is uncertain.
- Keep the source path and raw-ish metadata needed for a human to find the
  original material.
- Use low confidence and parse warnings when user/assistant boundaries are
  inferred.
- Prefer labeled, scored, and longer records when sampling for agent analysis.
