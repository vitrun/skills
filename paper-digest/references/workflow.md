# Paper Digest Workflow Details

## Preflight

Load config and inspect publish readiness:

```bash
PAPER_DIGEST_CONFIG="${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}"
[ -f "$PAPER_DIGEST_CONFIG" ] && . "$PAPER_DIGEST_CONFIG"
printf 'fetch=%s\ndoc=%s\nurl=%s\nanchor=%s\nchat=%s\n' \
  "${PAPER_DIGEST_FETCH_SCRIPT:-}" \
  "${PAPER_DIGEST_DOC_TOKEN:-}" \
  "${PAPER_DIGEST_DOC_URL:-}" \
  "${PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID:-}" \
  "${PAPER_DIGEST_NOTIFY_CHAT_ID:-}"
```

Resolve the fetcher:

```bash
PAPER_DIGEST_FETCH_SCRIPT="${PAPER_DIGEST_FETCH_SCRIPT:-paper-digest/scripts/fetch-alphaxiv-hot.py}"
python3 "$PAPER_DIGEST_FETCH_SCRIPT" --help
```

The bundled fetcher supports `--limit`, `--interval`, `--sort`, `--output md|json`, `--cache-dir`, `--no-cache`, `--no-cache-write`, and `--no-filter`.

## Preview

Produce JSON first:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --cache-dir "$PAPER_DIGEST_CACHE_DIR" \
  --no-cache-write \
  --output json > preview.json
```

Then Markdown:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --cache-dir "$PAPER_DIGEST_CACHE_DIR" \
  --no-cache-write \
  --output md > digest.md
```

If `preview.json` has `filtered_count == 0`, skip document publishing and send the no-updates notification. Do not insert a "no new papers" digest unless the user asks for an audit trail.

## Filtering

Keep AI/ML papers with useful research or product relevance. Prefer LLMs, agents, multimodal models, developer tooling, evaluation, data, inference, infrastructure, and applied AI systems.

Filter out papers that are outside scope, duplicates from local cache, or low-value for the digest audience. Use the local cache directory when available, but do not commit cache files.

## Publish

Require:

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

## Dedupe State

Only after publish succeeds:

```bash
mkdir -p "$PAPER_DIGEST_CACHE_DIR"
jq -r '.papers[].arxiv_id // empty' preview.json >> "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt"
sort -u "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt" -o "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt"
```

## Notify

For any publish, scheduled, or automation run, send a concise notification after the run finishes:

- Success: number of fetched, filtered, and published papers.
- No updates: no new papers matched after dedupe/filtering.
- Failure: failing step plus command, missing config key, or permission to check.

Use `lark-im` or `lark-cli im +messages-send`:

```bash
lark-cli im +messages-send \
  --as "${PAPER_DIGEST_NOTIFY_AS:-user}" \
  --chat-id "$PAPER_DIGEST_NOTIFY_CHAT_ID" \
  --text "Paper Digest: success
Window: 7 Days
Published: 5
Document: $PAPER_DIGEST_DOC_URL"
```

Implement with `try/finally`, shell `trap`, or equivalent so notification is attempted after fetch, filter, format, or publish failures. Capture the original failure first; if notification also fails, report both locally.

Notification content must not include raw access tokens, app secrets, full local paths, or personal identifiers. Every notification must include the configured document link.
