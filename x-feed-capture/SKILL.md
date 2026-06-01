---
name: x-feed-capture
description: Capture, filter, summarize, and publish high-value posts from an authenticated X/Twitter home feed. Use when the user asks to fetch X feed updates, collect AI/technology posts from X, continue from the previous X feed fetch, or write an X feed digest to a Lark/Feishu document.
---

# X Feed Capture

## Overview

Collect recent high-value X posts from the user's authenticated following feed, filter them by editorial judgment, publish a concise digest, and update a local continuation marker.

Do not hardcode or commit private document IDs, chat IDs, user paths, account names, cookies, or tokens. Read them from environment variables, local config, or the user's explicit prompt.

## Dependencies

This workflow requires local browser automation and, when publishing, Lark/Feishu automation.

Required for capture:

- Kimi WebBridge or a protocol-compatible local bridge running on `KIMI_WEBBRIDGE_URL`.
- A browser extension connected to that bridge and logged into X, ideally in the user's normal Chrome profile so the real authenticated Following feed is reused.
- An agent skill or local documentation for the bridge, such as `kimi-webbridge` or `qweb-bridge`.

Required for publishing:

- `lark-cli` plus the Lark agent skills `lark-shared`, `lark-doc`, and optionally `lark-im`.
- An authenticated Lark/Feishu session with scopes for document updates and optional messages.
- Destination values supplied by environment variables or the user's prompt.

Before running the workflow, check dependencies:

```bash
find "${CODEX_HOME:-$HOME/.codex}/skills" "$HOME/.config/agents/skills" "$HOME/.agents/skills" \
  -maxdepth 2 -name SKILL.md 2>/dev/null | grep -E '/(kimi-webbridge|qweb-bridge|lark-doc|lark-im|lark-shared)/SKILL.md' || true

command -v lark-cli || true
~/.kimi-webbridge/bin/kimi-webbridge status 2>/dev/null || curl -s --max-time 5 "${KIMI_WEBBRIDGE_URL:-http://127.0.0.1:10086}/status" || true
```

If bridge dependencies are missing, do not proceed to X. Offer to install Kimi WebBridge with the official installer:

```bash
curl -fsSL https://cdn.kimi.com/webbridge/install.sh | bash
```

After installation, have the user complete any browser extension or desktop-app connection steps, then re-run the health check. A compatible open-source alternative is QWebBridge; install it only if the user accepts substituting it for Kimi WebBridge.

If Lark dependencies are missing and publishing is requested, offer to install and configure the official Lark CLI:

```bash
npx @larksuite/cli@latest install
npx skills add larksuite/cli -g -y -a codex -s lark-shared lark-doc lark-im
lark-cli config init --new
lark-cli auth login --recommend
lark-cli auth status
```

Some commands open browser authorization pages. Surface the URL to the user and wait for them to finish authorization before continuing.

## Configuration

Use these names when available:

```bash
KIMI_WEBBRIDGE_URL="${KIMI_WEBBRIDGE_URL:-http://127.0.0.1:10086}"
X_FEED_STATE_FILE="${X_FEED_STATE_FILE:-$HOME/.x_feed_last_fetch}"
LARK_DOC_TOKEN="${LARK_DOC_TOKEN:?set the destination document token}"
LARK_DOC_URL="${LARK_DOC_URL:?set the destination document URL for notifications}"
LARK_DOC_ANCHOR_BLOCK_ID="${LARK_DOC_ANCHOR_BLOCK_ID:?set the block to insert after}"
LARK_NOTIFY_CHAT_ID="${LARK_NOTIFY_CHAT_ID:-}"
```

If a required value is missing, ask the user for that value or where to find local config. Never substitute a private value from a public skill file.

If `~/.config/x-feed-capture/config.env` is missing and the user did not explicitly ask for a dry run, do **not** silently continue without publishing. Treat this as a bootstrap gap and proactively guide the user through creating durable config before capture proceeds.

### Lark target bootstrap

When publishing is requested and `LARK_DOC_TOKEN`, `LARK_DOC_URL`, `LARK_DOC_ANCHOR_BLOCK_ID`, or `LARK_NOTIFY_CHAT_ID` is missing, guide the user through a one-time bootstrap with `lark-cli` instead of guessing IDs.

Preferred agent behavior when the durable config file is missing:

1. Tell the user the publish target is not configured yet.
2. Point them to the bundled bootstrap helper first, instead of only describing the manual flow.
3. Offer or run the helper with concrete arguments when the document URL, anchor text, or chat name is already known from local context or the prompt.
4. Only fall back to a dry run if the user explicitly asks for dry run behavior or declines bootstrap for now.

If this skill is available locally, prefer the bundled bootstrap helper:

```bash
/Users/axel/Work/skills/x-feed-capture/bin/bootstrap-x-feed-lark-targets.sh --help
```

Recommended acquisition flow:

1. **Document token**
   - Easiest path: ask the user for the destination document URL, save it as `LARK_DOC_URL`, and extract the token from `/docx/<token>` or `/wiki/<token>`.
   - If the document does not exist yet, create it first with `lark-cli docs +create --api-version v2`, then record the returned `document_id` as `LARK_DOC_TOKEN`; if no URL is returned, ask the user for the final browser URL before enabling notifications.

2. **Anchor block ID**
   - Fetch the document with block IDs:

   ```bash
   lark-cli docs +fetch --api-version v2 \
     --doc "$LARK_DOC_TOKEN" \
     --detail with-ids
   ```

   - Choose a stable insertion anchor near the top of the document, such as a fixed heading or intro paragraph, and record that block's `id="blk..."` as `LARK_DOC_ANCHOR_BLOCK_ID`.
   - Prefer a dedicated heading like `X Feed` or `Latest Captures` over anchoring to a frequently edited paragraph.

3. **Notify chat ID**
   - If notifications are desired, locate the target chat by name:

   ```bash
   lark-cli im +chat-search --as user --query "chat name"
   ```

   - Record the returned `chat_id` (`oc_...`) as `LARK_NOTIFY_CHAT_ID`.
   - If the exact name is unclear, start with `lark-cli im +chat-list --as user` and narrow from there.

Initialization guidance:

- Do the bootstrap under `--as user` unless the destination document/chat is explicitly bot-owned.
- If the user has not completed user authorization yet, run `lark-cli auth login --scope "docx:document:readonly docx:document:write_only im:chat:read im:message:send_as_user" --no-wait --json`, surface the verification URL, and resume after authorization completes.
- After collecting the three values, immediately validate them with a dry run or read call before the first production capture.

Recommended validation:

```bash
lark-cli docs +fetch --api-version v2 --as user --doc "$LARK_DOC_TOKEN" --detail with-ids
lark-cli im +chat-search --as user --query "expected chat name"
```

Storage recommendation:

- Do **not** treat these values as cache entries and do **not** put them under `~/.cache`; they are durable user configuration, not disposable runtime artifacts.
- Do **not** write them into automation memory markdown.
- Prefer a dedicated per-user config file such as `~/.config/x-feed-capture/config.env` with file mode `600`.
- Keep the file as simple shell env syntax so the automation can source it:

```bash
mkdir -p ~/.config/x-feed-capture
cat > ~/.config/x-feed-capture/config.env <<'EOF'
LARK_DOC_TOKEN=doxcnxxxxxxxxxxxx
LARK_DOC_URL=https://example.feishu.cn/wiki/doxcnxxxxxxxxxxxx
LARK_DOC_ANCHOR_BLOCK_ID=blkcnxxxxxxxxxxxx
LARK_NOTIFY_CHAT_ID=oc_xxxxxxxxxxxx
EOF
chmod 600 ~/.config/x-feed-capture/config.env
```

- Before running the workflow, source that file if it exists:

```bash
[ -f ~/.config/x-feed-capture/config.env ] && . ~/.config/x-feed-capture/config.env
```

If the user manages multiple destinations, keep one env file per destination, for example `~/.config/x-feed-capture/prod.env` and `~/.config/x-feed-capture/test.env`, and choose explicitly before running the capture.

## Workflow

### 1. Run dependency preflight

Verify the bridge skill, bridge daemon, browser extension connection, and Lark tooling before doing work with side effects.

If the bridge is missing or unhealthy, install or start it first. If publishing is requested but `lark-cli` or required Lark skills are missing, install and authenticate Lark first. If the user only wants a dry run, Lark can be skipped.

Before moving on, explicitly check whether durable publish config is present:

```bash
[ -f ~/.config/x-feed-capture/config.env ] && . ~/.config/x-feed-capture/config.env
printf 'doc=%s\nurl=%s\nanchor=%s\nchat=%s\n' "${LARK_DOC_TOKEN:-}" "${LARK_DOC_URL:-}" "${LARK_DOC_ANCHOR_BLOCK_ID:-}" "${LARK_NOTIFY_CHAT_ID:-}"
```

If the file is missing, or `LARK_DOC_TOKEN` / `LARK_DOC_URL` / `LARK_DOC_ANCHOR_BLOCK_ID` is empty, pause the capture workflow and bootstrap first unless the user explicitly requested a dry run. Prefer this helper:

```bash
/Users/axel/Work/skills/x-feed-capture/bin/bootstrap-x-feed-lark-targets.sh --help
```

If you already know enough inputs, run the helper directly instead of stopping at `--help`. For example:

```bash
/Users/axel/Work/skills/x-feed-capture/bin/bootstrap-x-feed-lark-targets.sh \
  --doc-url "https://example.feishu.cn/docx/..." \
  --anchor-text "X Feed" \
  --chat-name "AI Digest"
```

Do not discover missing config, continue with capture, and only mention bootstrap afterward. Missing durable config is an actionable setup task that should be surfaced immediately.

### 2. Check the browser bridge

Before any browser command, verify the configured bridge is healthy:

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
```

Continue only if the response indicates the daemon is OK and the browser extension/session is connected. If not, restart or ask the user to start the bridge. Do not continue with commands that would silently fail.

Use the configured logged-in browser bridge for X so the user's existing session is reused. Do not switch to unrelated browser automation unless the user explicitly changes the tool choice.

When using bridge `evaluate`, remember that the return shape may be a wrapper object such as `{"type":"string","value":"..."}` rather than a raw primitive. Inspect `.value` before dereferencing strings, arrays, or serialized JSON.

### 3. Read continuation state

Read the previous marker if present:

```bash
cat "$X_FEED_STATE_FILE" 2>/dev/null
```

Expected format:

```text
LAST_TIME=YYYY-MM-DD HH:MM
LAST_HREF=https://x.com/<user>/status/<id>
```

Use `LAST_TIME` and `LAST_HREF` to avoid duplicate posts. Missing state means this is the first run.

### 4. Open or reuse the real X Following tab

Prefer reusing an already-open X tab in the user's real browser session, especially when the user says to use Chrome, the current tab, or an existing X window:

```bash
curl -s -X POST "$KIMI_WEBBRIDGE_URL/command" \
  -H 'Content-Type: application/json' \
  -d '{"action":"find_tab","args":{"url":"https://x.com/home","active":true},"session":"x-feed"}'
```

If `find_tab` reports no open match, open a dedicated X tab:

```bash
curl -s -X POST "$KIMI_WEBBRIDGE_URL/command" \
  -H 'Content-Type: application/json' \
  -d '{"action":"navigate","args":{"url":"https://x.com/home","newTab":true},"session":"x-feed"}'
```

Wait for the page to load, then switch to the `Following` tab. Do not use the default `For you` tab for this workflow unless the user explicitly asks for algorithmic recommendations.

After switching, confirm:

- `location.href` is on X home.
- The `Following` tab has `aria-selected="true"`.
- The visible timeline is not a login page.
- The page is showing the user's normal feed cards, not only a repeated top-of-feed viewport.

If a `See new posts` button is visible, click it before extraction. Keep all later bridge commands in the same bridge session.

### 5. Scroll and extract posts

Loop through scroll/extract rounds until one of these conditions is met:

- At least 120 unique raw status links were collected.
- 80 scroll rounds have run.
- Eight consecutive extraction rounds produced no new status links and scroll position is still changing.

Prefer absolute-position scrolling over tiny incremental `scrollBy` steps. X's virtual timeline often re-renders the same visible cards if the agent only nudges the viewport.

Recommended pattern:

- Scroll to absolute Y positions in larger jumps, such as `0`, `1600`, `3200`, `4800`, ...
- Wait about `2.0-3.0s` after each jump so X has time to hydrate the next batch.
- After each round, record both `window.scrollY` and `document.body.scrollHeight`.
- Treat increasing `document.body.scrollHeight` as evidence that the timeline is actually loading deeper content.

If `scrollY` changes but the visible canonical status links barely change for several rounds, do not assume the feed is exhausted yet. First try deeper absolute jumps and longer waits. In practice, this is often the difference between collecting only a handful of links and collecting a full feed slice.

Extract visible `article[role=article]` elements, choose the first canonical link matching `https://x.com/<user>/status/<id>` exactly, and ignore `/analytics`, `/photo/`, `/video/`, and quoted-post media sublinks.

Deduplicate by canonical `href`. Keep raw extraction separate from final digest text.

Keep extraction scripts evaluator-friendly. Prefer simple DOM walking plus straightforward string checks over regex-heavy or syntax-dense page scripts. If `evaluate` starts throwing parser errors such as `SyntaxError: Unexpected token '^'`, simplify the page script first instead of adding more logic inside the page context.

Do not stop early just because a few rounds produced no new status links. X uses a virtual list and sometimes repeats the same visible articles while new content is loading. Ads may also occupy article slots; skip them and continue scrolling instead of treating them as evidence that extraction failed.

### 6. Enrich candidate details

Before ranking or writing the digest, open the status page for every candidate that is likely to be kept, and also for any raw item containing `Show more`. Extract the full article text from the detail page. Feed-card text is often truncated and can miss the actual point of the post.

Use detail enrichment to avoid summaries like "AI accounts list" when the full post contains the important claim, such as a title change, release detail, repository name, benchmark result, or setup instructions.

### 7. Filter and rank manually

Use judgment, not only JavaScript keyword matching.

Keep posts with meaningful information density, especially:

- AI, ML, agents, developer tools, infrastructure, product launches, technical analysis, and research.
- High-value technology, business, academic, or design content outside AI.

Exclude:

- Pure jokes, memes, low-context quips, engagement bait, and low-information links.
- Emotional venting, vulgar content, flamebait, and culture-war or political content.
- Posts already covered by the continuation marker or clearly older than `LAST_TIME`.

Rank candidates by AI/technology relevance, engagement, recency, and author credibility. Keep only the strongest items for the digest.

### 8. Publish to Lark/Feishu

Prefer the installed `lark-doc` skill or a configured `lark-cli`. Insert the new digest immediately after the configured anchor block so the newest batch appears near the top.

Use `block_insert_after`. Do not use append or string replacement for this workflow.

When using `lark-cli docs +update --api-version v2`, prefer the explicit update form:

```bash
lark-cli docs +update --api-version v2 \
  --as user \
  --doc "$LARK_DOC_TOKEN" \
  --command block_insert_after \
  --block-id "$LARK_DOC_ANCHOR_BLOCK_ID" \
  --content '<h2>...</h2><p>...</p>'
```

Do not rely on the short `--mode` interface shown in some help output. In practice, the stable path for this workflow is `--command ... --block-id ... --content ...`.

If the configured anchor is the document title block itself, inserting after that title block is acceptable and keeps the newest capture at the top. Validate the chosen anchor once with `docs +fetch --api-version v2 --detail with-ids` and then keep reusing it.

Digest structure:

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
- Escape or remove malformed text before sending XML/HTML-like content to the document API.
- When assembling XML/HTML through shell heredocs or interpolated strings, escape `$`-containing text or use single-quoted payload construction so summaries like `$20B+` are not mangled by shell expansion.

### 9. Notify

If `LARK_NOTIFY_CHAT_ID` or another configured destination is available, send a short success or failure message:

- Success: include fetched count, kept count, approximate time range, and `Document: $LARK_DOC_URL`.
- No updates: include the checked time range and `Document: $LARK_DOC_URL`.
- Failure: include the failing step, concrete recovery action, and `Document: $LARK_DOC_URL` when available.

Skip notification rather than inventing a destination. Do not send a success notification without the configured document link; run bootstrap first if `LARK_DOC_URL` is missing.

Preferred text shape:

```text
X Feed Capture: success
Fetched: 80
Kept: 8
Range: since last marker
Document: https://example.feishu.cn/wiki/...
```

### 10. Update continuation state

Only after a successful publish, overwrite the state file:

```bash
cat > "$X_FEED_STATE_FILE" <<EOF
LAST_TIME=$(date "+%Y-%m-%d %H:%M")
LAST_HREF=<canonical-status-url-used-as-marker>
EOF
```

Use `>` overwrite, never `>>` append.

Before updating the state file, do a quick verification read of the just-published section when feasible. If the inserted block contains shell-expansion damage, truncated text, or malformed XML rendering, repair the document first and only then advance `LAST_TIME` / `LAST_HREF`. The state marker is the commit point for this workflow.
