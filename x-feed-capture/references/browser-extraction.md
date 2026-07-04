# X Browser Extraction

## Browser Backend Health

Resolve the browser backend before opening X. Use the first healthy authenticated backend:

1. **DevTools dedicated profile** (`X_FEED_BROWSER_BACKEND=devtools` or `auto`): check `${X_FEED_DEVTOOLS_URL:-http://127.0.0.1:9222}/json/version`. If it is not listening and `X_FEED_DEVTOOLS_LAUNCHER` is executable, run that launcher and recheck. The profile must be a non-default Chrome profile logged into X.
2. **Kimi WebBridge** (`X_FEED_BROWSER_BACKEND=kimi` or `auto`): check `~/.kimi-webbridge/bin/kimi-webbridge status` or `${KIMI_WEBBRIDGE_URL:-http://127.0.0.1:10086}/status`. Continue only when the daemon and extension/session are connected.
3. **Chrome Apple Events** (`X_FEED_BROWSER_BACKEND=apple-events` or last `auto` fallback): use only when Chrome's `View > Developer > Allow JavaScript from Apple Events` is enabled and a small `execute javascript` probe succeeds.

Do not continue with commands that silently fail or return an empty page. If all backends fail, stop before capture and report a browser-control failure.

When using Kimi bridge `evaluate`, inspect wrapped return shapes such as `{"type":"string","value":"..."}` before dereferencing. When using DevTools, use `Runtime.evaluate` against the X page target returned by `/json/list`; do not read cookies or browser profile storage.

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

### Preferred: Chrome DevTools Dedicated Profile

Use a persistent non-default profile. If needed, start it with:

```bash
"${X_FEED_DEVTOOLS_LAUNCHER:-$HOME/.chrome-profiles/x-feed-debug/start-x-feed-debug-chrome.sh}"
```

Then verify and locate an X page target:

```bash
curl -s --max-time 5 "${X_FEED_DEVTOOLS_URL:-http://127.0.0.1:9222}/json/version"
curl -s --max-time 5 "${X_FEED_DEVTOOLS_URL:-http://127.0.0.1:9222}/json/list"
```

If no `type:"page"` target for `https://x.com/` exists, open one:

```bash
curl -s --max-time 5 -X PUT \
  "${X_FEED_DEVTOOLS_URL:-http://127.0.0.1:9222}/json/new?https://x.com/home"
```

Use the page target's `webSocketDebuggerUrl` with the Chrome DevTools Protocol. Confirm the page title or body indicates authenticated X home, for example `Home / X`, normal timeline tabs, and feed articles. If it shows the X landing/login page, stop and ask the user to log into the dedicated profile once.

### Fallback: Kimi WebBridge

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

### Last Fallback: Chrome Apple Events

Use Apple Events only after DevTools and Kimi are unavailable. First run a minimal probe:

```applescript
tell application "Google Chrome"
  execute active tab of front window javascript "JSON.stringify({href: location.href, title: document.title})"
end tell
```

If Chrome reports that JavaScript from Apple Events is disabled even when the menu appears checked, treat that backend as failed instead of retrying extraction.

Switch to the Following tab, then confirm:

- `location.href` is on X home.
- Following has `aria-selected="true"`.
- The visible page is not a login page.
- The feed cards are normal user feed content, not only repeated top-of-feed content.

If a `See new posts` button is visible, click it before extraction.

## Following Scroll And Extract

Loop until one condition is met:

- at least 120 unique raw status links were collected;
- the previous `LAST_HREF` marker was found in the Following slice;
- reliable exhaustion is proven by eight consecutive rounds with no new status links and no meaningful timeline progress.

If 80 scroll rounds have run without hitting another stop condition, stop capturing to avoid an unbounded browser session, then classify the output using the health rules below. The round cap alone is not proof of reliable exhaustion.

Use incremental scrolling as the primary method. Do not use large absolute `window.scrollTo(0, N)` jumps for the main pass; X can update `scrollY` while its virtualized timeline keeps repeating the same visible cards.

- sample once at the top after selecting Following;
- if `See new posts` is visible, click it and sample again;
- each round dispatches a wheel event and then calls `window.scrollBy(0, 700-1000)`;
- wait about `1.5-2.5s` after each round;
- record `window.scrollY`, `document.body.scrollHeight`, visible article count, per-round canonical status URLs, cumulative unique status URLs, and whether `LAST_HREF` appeared;
- treat increasing unique canonical status URLs as the primary health signal. Increasing `scrollY` or `document.body.scrollHeight` alone is not enough.

Reliable exhaustion requires the visible timeline to stop progressing: no new canonical links, little or no `scrollY` movement, and little or no `document.body.scrollHeight` growth for the final rounds. If `scrollY` changes but canonical links barely change, treat it as a suspect extraction, not exhaustion.

Extract visible `article[role=article]` elements. Choose the first canonical link matching `https://x.com/<user>/status/<id>`. Ignore `/analytics`, `/photo/`, `/video/`, and quoted-post media sublinks.

Keep extraction scripts evaluator-friendly. Prefer DOM walking and string checks over dense regex. If `evaluate` throws parser errors, simplify the page script before adding logic.

### Extraction Health And Recovery

Before publishing, classify the raw capture:

- **healthy**: unique canonical links keep increasing during scroll, or the previous `LAST_HREF` marker was reached.
- **complete enough**: at least 120 unique links were collected even if the marker was not reached.
- **suspect**: fewer than 20 unique Following links were collected, the marker was not reached, and scroll position changed; or multiple rounds show the same canonical link set while article cards are visible; or visible article count is nonzero but canonical link extraction is near zero.

For a suspect capture:

1. Open a fresh `https://x.com/home` tab/session, reselect Following, click `See new posts` if present, and rerun the incremental wheel/`scrollBy` pass.
2. If the recovery pass produces materially more links, discard the suspect raw pass and continue from the recovery output.
3. If recovery is still suspect, do not publish as a normal success and do not advance `LAST_TIME` / `LAST_HREF`. Report the run as degraded and include the per-round evidence.

When a previous run is discovered to have advanced state after a suspect capture, use the last known pre-suspect marker as the correction baseline for the next repair run. Publish the correction batch only after normal destination verification and notification.

## Optional For You Discovery

When the user has requested For You coverage or `X_FEED_INCLUDE_FOR_YOU=1`:

- finish the Following pass first;
- switch back to the For You tab and confirm it has `aria-selected="true"`;
- collect about five to eight incremental wheel/`scrollBy` rounds;
- wait about `1.5-2.5s` after each round;
- extract canonical status URLs with the same article parser;
- merge these candidates into the same pool as Following candidates and de-duplicate by canonical status URL.

Do not treat For You as a second continuation stream unless the user explicitly asks for that. It is a small exploration/discovery sample, so it can surface useful off-graph items but should not advance or overwrite the main marker.

## Enrichment And Ranking

Open detail pages for likely kept candidates and any card containing `Show more`. Feed-card text can be truncated and miss the core claim.

A clear feed-card title is enough to pass the initial keep gate. If the visible title names a concrete developer tool, CLI/version release, technical report, benchmark, model, paper, product launch, or agent-infrastructure claim, keep it as a candidate and enrich it before deciding whether to exclude it. For You items are allowed to enter this gate; do not downrank or drop them solely because they are supplemental discovery rather than the continuation source.

Keep posts with meaningful information density:

- AI, ML, agents, developer tools, infrastructure, product launches, technical analysis, and research.
- High-value technology, business, academic, or design content outside AI.

Exclude:

- jokes, memes, low-context quips, engagement bait, and low-information links;
- emotional venting, vulgar content, flamebait, culture-war, or political content;
- Following posts already covered by `LAST_TIME` / `LAST_HREF`;
- duplicate For You posts already captured from Following.

Rank by relevance, recency, engagement, author credibility, and novelty. Blend Following and For You items into one digest unless the user asks to label or separate sources.

Ranking is not an implicit top-N cap. Unless the prompt or local preferences specify a maximum digest size, keep all candidates that satisfy the keep policy and local preferences. Do not drop relevant high-signal posts solely to make the digest shorter.
