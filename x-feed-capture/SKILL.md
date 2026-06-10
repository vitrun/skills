---
name: x-feed-capture
description: Capture, filter, summarize, and publish high-value posts from an authenticated X/Twitter home feed. Use when the user asks to fetch X feed updates, collect AI/technology posts from X, continue from the previous X feed fetch, or write an X feed digest to a Lark/Feishu document.
---

# X Feed Capture

Collect recent high-value X posts from the user's authenticated Following feed, filter them by editorial judgment, publish a concise digest, and update a local continuation marker.

Do not hardcode or commit private document IDs, chat IDs, user paths, account names, cookies, or tokens. Read them from environment variables, local config, or the user's explicit prompt.

## Resource Map

- Read [references/setup.md](references/setup.md) for dependencies, durable config, and one-time Lark bootstrap.
- Read [references/browser-extraction.md](references/browser-extraction.md) before opening X or writing extraction code.
- Read [references/lark-publish.md](references/lark-publish.md) before publishing, notifying, or advancing state.
- Read [references/gotchas.md](references/gotchas.md) when a bridge, Lark CLI, X scrolling, or state marker failure appears.
- Prefer the bundled bootstrap helper for missing publish config: [bin/bootstrap-x-feed-lark-targets.sh](bin/bootstrap-x-feed-lark-targets.sh).

## Non-Negotiables

- Use the real authenticated browser session. Do not switch to unauthenticated scraping or a different browser stack unless the user asks.
- Use the Following feed, not For You, unless the user explicitly requests algorithmic recommendations.
- Missing durable publish config is a setup task, not a reason to silently downgrade to local dry run.
- Keep raw extraction, candidate enrichment, ranking, digest writing, publish verification, notification, and state advancement as separate steps.
- Advance `LAST_TIME` / `LAST_HREF` only after publish, verification, and notification have succeeded or after the user explicitly accepts a no-notification run.

## Workflow

1. **Preflight and config**
   - Load `~/.config/x-feed-capture/config.env` if present.
   - Verify Kimi WebBridge or a compatible bridge is healthy.
   - If publishing is intended and config is incomplete, bootstrap first. See [references/setup.md](references/setup.md).

2. **Read continuation state**
   - Read `${X_FEED_STATE_FILE:-$HOME/.x_feed_last_fetch}`.
   - Treat missing state as a first run.

3. **Open X Following**
   - Reuse an existing authenticated X tab when available.
   - Otherwise open `https://x.com/home` in the configured bridge session.
   - Confirm the page is logged in and the Following tab is selected. See [references/browser-extraction.md](references/browser-extraction.md).

4. **Capture raw candidates**
   - Scroll with large absolute jumps and waits.
   - Collect canonical `https://x.com/<user>/status/<id>` links from article cards.
   - Stop only after enough unique links or clear exhaustion according to [references/browser-extraction.md](references/browser-extraction.md).

5. **Enrich and rank**
   - Open likely kept status pages, especially cards with `Show more`.
   - Filter manually for information density, AI/technology relevance, recency, author credibility, and novelty relative to the continuation marker.

6. **Publish and notify**
   - Insert the digest after `LARK_DOC_ANCHOR_BLOCK_ID`.
   - Verify the inserted section before claiming success.
   - Send a concise success, no-update, or failure notification with `Document: $LARK_DOC_URL`.
   - See [references/lark-publish.md](references/lark-publish.md).

7. **Commit state**
   - Overwrite the continuation state file only after the publish path is verified.
   - Use `>` overwrite, never `>>` append.

## Final Report

Report:

- fetched raw link count
- kept/published item count
- continuation marker action
- publish/notification status
- recovered errors and any remaining follow-up
