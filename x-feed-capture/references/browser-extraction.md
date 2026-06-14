# X Browser Extraction

## Bridge Health

Before browser commands:

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
```

Continue only when the daemon and extension/session are connected. Do not continue with commands that would silently fail.

When using bridge `evaluate`, inspect wrapped return shapes such as `{"type":"string","value":"..."}` before dereferencing.

## Continuation State

Read previous marker:

```bash
cat "$X_FEED_STATE_FILE" 2>/dev/null
```

Expected format:

```text
LAST_TIME=YYYY-MM-DD HH:MM
LAST_HREF=https://x.com/<user>/status/<id>
```

Use both values to avoid duplicates in the Following pass. The marker may appear inside the captured slice, not only before it.

For You is a supplemental discovery source when enabled by prompt or `X_FEED_INCLUDE_FOR_YOU=1`. It may not expose a stable chronological anchor, so do not use it to decide or update `LAST_TIME` / `LAST_HREF`.

## Open Or Reuse X

Prefer an existing authenticated tab:

```bash
curl -s -X POST "$KIMI_WEBBRIDGE_URL/command" \
  -H 'Content-Type: application/json' \
  -d '{"action":"find_tab","args":{"url":"https://x.com/home","active":true},"session":"x-feed"}'
```

If no matching tab exists, open one:

```bash
curl -s -X POST "$KIMI_WEBBRIDGE_URL/command" \
  -H 'Content-Type: application/json' \
  -d '{"action":"navigate","args":{"url":"https://x.com/home","newTab":true},"session":"x-feed"}'
```

Switch to the Following tab, then confirm:

- `location.href` is on X home.
- Following has `aria-selected="true"`.
- The visible page is not a login page.
- The feed cards are normal user feed content, not only repeated top-of-feed content.

If a `See new posts` button is visible, click it before extraction.

## Following Scroll And Extract

Loop until one condition is met:

- at least 120 unique raw status links were collected;
- 80 scroll rounds have run;
- eight consecutive extraction rounds produced no new status links and scroll position is still changing.

Prefer absolute scrolling over tiny `scrollBy` steps:

- jump to `0`, `1600`, `3200`, `4800`, ...
- wait about `2.0-3.0s` after each jump;
- record `window.scrollY` and `document.body.scrollHeight`;
- treat increasing `document.body.scrollHeight` as evidence that X is loading deeper content.

If `scrollY` changes but canonical links barely change, try deeper jumps and longer waits before declaring exhaustion.

Extract visible `article[role=article]` elements. Choose the first canonical link matching `https://x.com/<user>/status/<id>`. Ignore `/analytics`, `/photo/`, `/video/`, and quoted-post media sublinks.

Keep extraction scripts evaluator-friendly. Prefer DOM walking and string checks over dense regex. If `evaluate` throws parser errors, simplify the page script before adding logic.

## Optional For You Discovery

When the user has requested For You coverage or `X_FEED_INCLUDE_FOR_YOU=1`:

- finish the Following pass first;
- switch back to the For You tab and confirm it has `aria-selected="true"`;
- collect about five absolute-scroll pages, for example `0`, `1600`, `3200`, `4800`, `6400`;
- wait about `2.0-3.0s` after each jump;
- extract canonical status URLs with the same article parser;
- merge these candidates into the same pool as Following candidates and de-duplicate by canonical status URL.

Do not treat For You as a second continuation stream unless the user explicitly asks for that. It is a small exploration/discovery sample, so it can surface useful off-graph items but should not advance or overwrite the main marker.

## Enrichment And Ranking

Open detail pages for likely kept candidates and any card containing `Show more`. Feed-card text can be truncated and miss the core claim.

Keep posts with meaningful information density:

- AI, ML, agents, developer tools, infrastructure, product launches, technical analysis, and research.
- High-value technology, business, academic, or design content outside AI.

Exclude:

- jokes, memes, low-context quips, engagement bait, and low-information links;
- emotional venting, vulgar content, flamebait, culture-war, or political content;
- Following posts already covered by `LAST_TIME` / `LAST_HREF`;
- duplicate For You posts already captured from Following.

Rank by relevance, recency, engagement, author credibility, and novelty. Blend Following and For You items into one digest unless the user asks to label or separate sources.
