# Paper Digest Destinations

## Selection

Resolve the destination before publishing or updating dedupe state:

```bash
[ -f "$HOME/.config/codex-delivery/preferences.env" ] && . "$HOME/.config/codex-delivery/preferences.env"
PAPER_DIGEST_CONFIG="${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}"
[ -f "$PAPER_DIGEST_CONFIG" ] && . "$PAPER_DIGEST_CONFIG"
PAPER_DIGEST_DESTINATION="${PAPER_DIGEST_DESTINATION:-${CODEX_DELIVERY_DESTINATION:-feishu}}"
```

Supported values:

- `feishu`: Lark/Feishu document insertion. See [workflow.md](workflow.md).
- `obsidian`: local Obsidian vault note. See [obsidian-publish.md](obsidian-publish.md).

Per-skill config should override the global delivery preference. A one-off explicit user instruction in the prompt overrides both.

## Publish Contract

Every destination must return or establish:

- `ok`: explicit success signal.
- `destination_ref`: a stable user-facing reference, such as a Feishu URL, Obsidian URI, or absolute note path.
- `verification`: proof that the just-produced digest was written.

Only after the destination contract succeeds may the workflow append paper IDs to `seen_ids.txt`.

## Notifications

Use destination-neutral text:

```text
Paper Digest: success
Window: 7 Days
Fetched: 20
Published: 5
Destination: <destination_ref>
```

For failure messages, include the failing step and the same destination reference when available. Do not expose local secrets, document tokens, chat IDs, API keys, or full private cache contents.
