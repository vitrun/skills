# X Feed Lark Publish

## Publish

Prefer `lark-doc` or configured `lark-cli`. Insert new content immediately after `LARK_DOC_ANCHOR_BLOCK_ID` so the newest batch stays near the top.

Use `block_insert_after`. Do not use append or string replacement for this workflow.

Stable update form:

```bash
lark-cli docs +update --api-version v2 \
  --as user \
  --doc "$LARK_DOC_TOKEN" \
  --command block_insert_after \
  --block-id "$LARK_DOC_ANCHOR_BLOCK_ID" \
  --content '<h2>...</h2><p>...</p>'
```

Do not rely on the short `--mode` interface shown in some help output. The reliable shape is `--command ... --block-id ... --content ...`.

If the configured anchor is the document title block, inserting after it is acceptable. Validate once with `docs +fetch --api-version v2 --detail with-ids`.

## Digest Structure

Use:

```html
<h2>YYYY-MM-DD HH:MM</h2>
<p>Fetched N posts and kept M high-value items.</p>
<h3>1. Author - concise title</h3>
<p>Summary under 100 Chinese characters or one short English sentence.</p>
<p>Likes: N Reposts: N <a href="https://x.com/user/status/id">Original</a></p>
<hr/>
```

Rules:

- Use one `h2` per batch.
- Use one `h3`, summary paragraph, metadata/link paragraph, and divider per item.
- Do not paste raw feed text containing garbled symbols or UI fragments.
- Do not mix heading, body, and link content on one line.
- Escape or remove malformed text before sending XML/HTML-like content.
- When building payloads in shell, avoid accidental `$` expansion in summaries.

## Notify

If `LARK_NOTIFY_CHAT_ID` is available, send a short status message:

- Success: fetched count, kept count, approximate time range, and `Destination: $LARK_DOC_URL`.
- No updates: checked time range and `Destination: $LARK_DOC_URL`.
- Failure: failing step, recovery action, and `Destination: $LARK_DOC_URL` when available.

Skip notification rather than inventing a destination. Do not send success without the configured document link; bootstrap first if `LARK_DOC_URL` is missing.

Preferred shape:

```text
X Feed Capture: success
Fetched: 80
Kept: 8
Range: since last marker
Destination: https://example.feishu.cn/wiki/...
```

## State Advancement

Only after successful publish and verification, overwrite the state file:

```bash
cat > "$X_FEED_STATE_FILE" <<EOF
LAST_TIME=$(date "+%Y-%m-%d %H:%M")
LAST_HREF=<canonical-status-url-used-as-marker>
EOF
```

Use `>` overwrite, never `>>` append.

Before updating state, verify the just-published section when feasible. If the inserted block contains shell-expansion damage, truncated text, or malformed rendering, repair the document first. The state marker is the commit point for this workflow.
