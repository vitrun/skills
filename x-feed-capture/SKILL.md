---
name: x-feed-capture
description: Capture, filter, summarize, and publish high-value posts from an authenticated X/Twitter home feed. Use when the user asks to fetch X feed updates, collect AI/technology posts from X, continue from the previous X feed fetch, or write an X feed digest to a configured destination such as Lark/Feishu or Obsidian.
---

# X Feed Capture

Collect recent high-value X posts from the user's authenticated Following feed, optionally blend in a small For You discovery sample, filter them by editorial judgment, publish a concise digest to the configured destination, and update a local continuation marker.

Do not hardcode or commit private document IDs, chat IDs, user paths, account names, cookies, or tokens. Read them from environment variables, local config, or the user's explicit prompt.

## Resource Map

- Read [references/setup.md](references/setup.md) for dependencies, durable config, destination preference, and one-time setup.
- Read [references/browser-extraction.md](references/browser-extraction.md) before opening X or writing extraction code.
- Read [references/destinations.md](references/destinations.md) before publishing, notifying, or advancing state.
- Read [references/lark-publish.md](references/lark-publish.md) for the Lark/Feishu destination.
- Read [references/obsidian-publish.md](references/obsidian-publish.md) for the Obsidian destination.
- Read [references/gotchas.md](references/gotchas.md) when a bridge, Lark CLI, X scrolling, or state marker failure appears.
- Prefer the bundled Feishu bootstrap helper for missing Feishu config: [bin/bootstrap-x-feed-lark-targets.sh](bin/bootstrap-x-feed-lark-targets.sh).

## Non-Negotiables

- Use the real authenticated browser session. Do not switch to unauthenticated scraping or a different browser stack unless the user asks.
- Use Following as the primary feed and continuation source. When the user has requested For You coverage or `X_FEED_INCLUDE_FOR_YOU=1`, treat For You as a small supplemental discovery sample, not as the state anchor.
- Missing durable destination config is a setup task, not a reason to silently downgrade to local dry run.
- Keep raw extraction, candidate enrichment, ranking, digest writing, publish verification, notification, and state advancement as separate steps.
- Treat notifications as a user preference. When notifications are enabled, advance `LAST_TIME` / `LAST_HREF` only after destination publish, destination verification, and the configured notification have succeeded. When notifications are disabled, do not send a notification and do not block state advancement on notification.

## Workflow

1. **Preflight and config**
   - Load `~/.config/x-feed-capture/config.env` if present.
   - If `X_FEED_PREFERENCES_FILE` is set, or `~/.config/x-feed-capture/preferences.md` exists, read that local preference file and apply it as user-specific editorial guidance.
   - Resolve `X_FEED_DESTINATION` from explicit env, per-skill config, or global delivery preference. Default to `feishu` for backward compatibility.
   - Resolve `X_FEED_NOTIFY`; default to enabled only when a notification target such as `LARK_NOTIFY_CHAT_ID` is configured, and respect `X_FEED_NOTIFY=0` as an explicit opt-out.
   - Resolve the browser backend. Prefer a dedicated Chrome DevTools profile when configured; otherwise use Kimi WebBridge, then Chrome Apple Events only as a last fallback. See [references/browser-extraction.md](references/browser-extraction.md).
   - If publishing is intended and config is incomplete, bootstrap first. See [references/setup.md](references/setup.md).

2. **Read continuation state**
   - Read `${X_FEED_STATE_FILE:-$HOME/.x_feed_last_fetch}`.
   - Treat missing state as a first run.

3. **Open X Following**
   - Reuse or launch the configured authenticated browser backend.
   - Open `https://x.com/home` in that backend.
   - Confirm the page is logged in and the Following tab is selected. See [references/browser-extraction.md](references/browser-extraction.md).

4. **Capture raw candidates**
   - Capture with incremental wheel/`scrollBy` rounds, not large absolute jumps. X's virtualized timeline can move `scrollY` while repeating the same cards if absolute `scrollTo` is used.
   - Collect canonical `https://x.com/<user>/status/<id>` links from article cards.
   - Record per-round scroll position, scroll height, visible article count, per-round canonical links, cumulative unique links, and whether the previous `LAST_HREF` was seen.
   - Stop only after enough unique links, the previous marker is reached, or reliable exhaustion is proven according to [references/browser-extraction.md](references/browser-extraction.md). A low raw count while `scrollY` changes is not reliable exhaustion.
   - If extraction health is suspect, run the recovery pass before publishing. Do not advance state after a degraded capture unless the user explicitly accepts the gap.
   - If For You coverage is enabled by prompt or `X_FEED_INCLUDE_FOR_YOU=1`, switch to For You after the Following pass and use the same incremental wheel/`scrollBy` extraction for a small discovery sample. Merge those candidates into the same raw candidate pool, de-duplicated by canonical status URL.

5. **Enrich and rank**
   - Open likely kept status pages, especially cards with `Show more`.
   - Filter manually for information density, AI/technology relevance, recency, author credibility, and novelty relative to the continuation marker where applicable.
   - Apply any loaded local preference file to resolve editorial questions such as breadth, topic emphasis, language preference, or keep policy.
   - Rank Following and For You candidates together unless the user explicitly asks for separate sections. For You is exploratory; do not require an exact prior marker for it.
   - Do not infer a fixed kept-item limit from the word "rank"; ranking orders eligible items, while filtering removes only items that fail the keep policy, local preferences, or exclusion rules.

6. **Publish and notify**
   - Publish to the configured destination.
   - Verify the inserted note or section before claiming success.
   - If notifications are enabled, send a concise success, no-update, or failure notification with the destination reference. If disabled, record `notification=disabled` in the final report.
   - See [references/destinations.md](references/destinations.md).

7. **Commit state**
   - Overwrite the continuation state file only after destination publish, verification, and any enabled configured notification are complete.
   - Use `>` overwrite, never `>>` append.

## Final Report

Report:

- fetched raw link count
- extraction health classification and whether recovery was needed
- kept/published item count
- continuation marker action
- destination publish/verification status
- notification status
- recovered errors and any remaining follow-up
