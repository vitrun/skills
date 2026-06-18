# X Feed Destinations

## Selection

Resolve the destination before capture work that will commit state:

```bash
[ -f "$HOME/.config/codex-delivery/preferences.env" ] && . "$HOME/.config/codex-delivery/preferences.env"
[ -f "$HOME/.config/x-feed-capture/config.env" ] && . "$HOME/.config/x-feed-capture/config.env"
X_FEED_DESTINATION="${X_FEED_DESTINATION:-${CODEX_DELIVERY_DESTINATION:-feishu}}"
```

Supported values:

- `feishu`: Lark/Feishu document insertion. See [lark-publish.md](lark-publish.md).
- `obsidian`: local Obsidian vault note. See [obsidian-publish.md](obsidian-publish.md).

Per-skill config should override the global delivery preference. A one-off explicit user instruction in the prompt overrides both.

## Publish Contract

Every destination must return or establish:

- `ok`: explicit success signal.
- `destination_ref`: a stable user-facing reference, such as a Feishu URL, Obsidian URI, or absolute note path.
- `verification`: proof that the just-produced batch was written, not just that a command exited.

Do not advance `LAST_TIME` / `LAST_HREF` until the destination contract is satisfied and any enabled configured notification succeeds. If `X_FEED_NOTIFY=0`, skip notification and record `notification=disabled` in the final report and automation memory.

## Notifications

Notifications are optional. Resolve `X_FEED_NOTIFY` from durable config before publishing:

- `0`: disabled; do not send success, no-update, or failure notifications.
- `1`: enabled; require a notification target such as `LARK_NOTIFY_CHAT_ID`.
- unset: enabled only when a notification target is configured.

When enabled, use destination-neutral text:

```text
X Feed Capture: success
Fetched: 80
Kept: 8
Range: since last marker
Destination: <destination_ref>
```

For failure messages, include the failing step and the same destination reference when available. Do not expose local secrets, document tokens, chat IDs, cookies, or browser profile details.
