# Paper Digest Workflow Details

## Preflight

Load config and inspect publish readiness:

```bash
[ -f "$HOME/.config/codex-delivery/preferences.env" ] && . "$HOME/.config/codex-delivery/preferences.env"
PAPER_DIGEST_CONFIG="${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}"
[ -f "$PAPER_DIGEST_CONFIG" ] && . "$PAPER_DIGEST_CONFIG"
PAPER_DIGEST_DESTINATION="${PAPER_DIGEST_DESTINATION:-${CODEX_DELIVERY_DESTINATION:-feishu}}"
printf 'destination=%s\nfetch=%s\ndoc=%s\nurl=%s\nanchor=%s\nchat=%s\nvault=%s\n' \
  "$PAPER_DIGEST_DESTINATION" \
  "${PAPER_DIGEST_FETCH_SCRIPT:-}" \
  "${PAPER_DIGEST_DOC_TOKEN:-}" \
  "${PAPER_DIGEST_DOC_URL:-}" \
  "${PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID:-}" \
  "${PAPER_DIGEST_NOTIFY_CHAT_ID:-}" \
  "${OBSIDIAN_VAULT_PATH:-}"
```

Resolve the fetcher:

```bash
PAPER_DIGEST_FETCH_SCRIPT="${PAPER_DIGEST_FETCH_SCRIPT:-paper-digest/scripts/fetch-alphaxiv-hot.py}"
PAPER_DIGEST_PREFERENCES_FILE="${PAPER_DIGEST_PREFERENCES_FILE:-$HOME/.config/paper-digest/preferences.json}"
python3 "$PAPER_DIGEST_FETCH_SCRIPT" --help
```

The bundled fetcher supports `--limit`, `--interval`, `--sort`, `--output md|json`, `--cache-dir`, `--no-cache`, and `--no-cache-write`.

## Preview

Produce raw candidate JSON first:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --cache-dir "$PAPER_DIGEST_CACHE_DIR" \
  --no-cache-write \
  --output json > raw-preview.json
```

Optionally render a candidate markdown view:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --cache-dir "$PAPER_DIGEST_CACHE_DIR" \
  --no-cache-write \
  --output md > candidate-digest.md
```

If `raw-preview.json` has `candidate_count == 0`, skip destination publishing and send the no-updates notification. Do not insert a "no new papers" digest unless the user asks for an audit trail.

## Preference Curation

Preference semantics belong to the skill or agent layer. The fetcher should not hardcode topic judgments.

When `PAPER_DIGEST_PREFERENCES_FILE` exists:

1. Read `interested` and `excluded` from that JSON file.
2. Review `raw-preview.json` semantically against those preferences.
3. Create a `selection.json` file following [selection-template.json](../assets/selection-template.json):

```json
{
  "preferences_applied": true,
  "preference_summary": "Agents and inference work prioritized; biology-heavy papers excluded.",
  "selected_papers": [
    {
      "arxiv_id": "2606.12345",
      "preference_score": 0.91,
      "why_selected": "Strong match to coding-agent evaluation and deployable systems."
    }
  ]
}
```

Then materialize the final publish artifacts:

```bash
python3 paper-digest/scripts/materialize-curated-digest.py \
  --raw-preview raw-preview.json \
  --selection-file selection.json \
  --output-json preview.json \
  --output-md digest.md \
  --date "$(date +%F)"
```

If no preference file exists, the agent may still curate manually, but `preview.json` must always be the final curated publish set.

If `preview.json` has `filtered_count == 0`, skip destination publishing and send the no-updates notification.

## Publish

Resolve destination behavior before publishing. See [destinations.md](destinations.md).

For `PAPER_DIGEST_DESTINATION=feishu`, require:

```bash
: "${PAPER_DIGEST_DOC_TOKEN:?set destination document token}"
: "${PAPER_DIGEST_DOC_URL:?set destination document URL}"
: "${PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID:?set destination anchor block id}"
```

Require `PAPER_DIGEST_NOTIFY_CHAT_ID` unless the user explicitly skips notification.

Insert after the configured anchor. Use a relative `@digest.md` path from the directory that contains the file; `lark-cli` rejects absolute `@/tmp/...` content paths.

```bash
(cd "$(dirname "$DIGEST_PATH")" && \
  lark-cli docs +update --api-version v2 \
    --as "${PAPER_DIGEST_DOC_AS:-user}" \
    --doc "$PAPER_DIGEST_DOC_TOKEN" \
    --command block_insert_after \
    --block-id "$PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID" \
    --doc-format markdown \
    --content @"$(basename "$DIGEST_PATH")" > publish.json)
jq -e '.ok == true' "$(dirname "$DIGEST_PATH")/publish.json" >/dev/null
```

Do not rely on `lark-cli` exit code alone. Some validation failures return JSON with `"ok": false` while the process exits successfully.

Do not rely on fetcher hardcoded document defaults. Publishing belongs in this workflow, not in the fetch script.

For `PAPER_DIGEST_DESTINATION=obsidian`, require:

```bash
: "${OBSIDIAN_VAULT_PATH:?set destination Obsidian vault path}"
```

Publish and verify with [obsidian-publish.md](obsidian-publish.md). Treat the readback checks as the Obsidian equivalent of `.ok == true`.

## Dedupe State

Only after destination publish and verification succeed:

```bash
mkdir -p "$PAPER_DIGEST_CACHE_DIR"
jq -r '.papers[].arxiv_id // empty' preview.json >> "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt"
sort -u "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt" -o "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt"
```

## Notify

For any publish, scheduled, or automation run, send a concise notification after the run finishes:

- Success: number of fetched, filtered, and published papers.
- No updates: no new papers remained after dedupe and preference curation.
- Failure: failing step plus command, missing config key, or permission to check.

Use `lark-im` or `lark-cli im +messages-send`:

```bash
lark-cli im +messages-send \
  --as "${PAPER_DIGEST_NOTIFY_AS:-user}" \
  --chat-id "$PAPER_DIGEST_NOTIFY_CHAT_ID" \
  --text "Paper Digest: success
Window: 7 Days
Published: 5
Destination: $destination_ref"
```

Implement with `try/finally`, shell `trap`, or equivalent so notification is attempted after fetch, filter, format, or publish failures. Capture the original failure first; if notification also fails, report both locally.

Notification content must not include raw access tokens, app secrets, full private cache paths, or personal identifiers. Every notification must include the configured destination reference.
