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
- A browser extension connected to that bridge and logged into X.
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
LARK_DOC_ANCHOR_BLOCK_ID="${LARK_DOC_ANCHOR_BLOCK_ID:?set the block to insert after}"
LARK_NOTIFY_CHAT_ID="${LARK_NOTIFY_CHAT_ID:-}"
```

If a required value is missing, ask the user for that value or where to find local config. Never substitute a private value from a public skill file.

## Workflow

### 1. Run dependency preflight

Verify the bridge skill, bridge daemon, browser extension connection, and Lark tooling before doing work with side effects.

If the bridge is missing or unhealthy, install or start it first. If publishing is requested but `lark-cli` or required Lark skills are missing, install and authenticate Lark first. If the user only wants a dry run, Lark can be skipped.

### 2. Check the browser bridge

Before any browser command, verify the configured bridge is healthy:

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
```

Continue only if the response indicates the daemon is OK and the browser extension/session is connected. If not, restart or ask the user to start the bridge. Do not continue with commands that would silently fail.

Use the configured logged-in browser bridge for X so the user's existing session is reused. Do not switch to unrelated browser automation unless the user explicitly changes the tool choice.

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

### 4. Open X Following and keep the tab ID

Navigate to X in a dedicated session and record the returned `tabId`:

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

If a `See new posts` button is visible, click it before extraction. All later bridge commands must include the same `tabId`.

### 5. Scroll and extract posts

Loop through scroll/extract rounds until one of these conditions is met:

- At least 120 unique raw status links were collected.
- 80 scroll rounds have run.
- Eight consecutive extraction rounds produced no new status links and scroll position is still changing.

Use about `700-900px` per scroll with a short wait between rounds. Extract visible `article[role=article]` elements, choose the first canonical link matching `https://x.com/<user>/status/<id>` exactly, and ignore `/analytics`, `/photo/`, `/video/`, and quoted-post media sublinks.

Deduplicate by canonical `href`. Keep raw extraction separate from final digest text.

Do not stop early just because a few rounds produced no new status links. X uses a virtual list and sometimes repeats the same visible articles while new content is loading.

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

### 9. Notify

If `LARK_NOTIFY_CHAT_ID` or another configured destination is available, send a short success or failure message:

- Success: include fetched count, kept count, and approximate time range.
- Failure: include the failing step and the concrete recovery action.

Skip notification rather than inventing a destination.

### 10. Update continuation state

Only after a successful publish, overwrite the state file:

```bash
cat > "$X_FEED_STATE_FILE" <<EOF
LAST_TIME=$(date "+%Y-%m-%d %H:%M")
LAST_HREF=<canonical-status-url-used-as-marker>
EOF
```

Use `>` overwrite, never `>>` append.
