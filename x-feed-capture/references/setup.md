# X Feed Capture Setup

## Dependencies

Capture requires one authenticated browser-control backend. Prefer them in this order:

1. **Chrome DevTools dedicated profile**: a non-default Chrome profile launched with `--remote-debugging-port`, logged into X once, and reused across runs. This is the preferred backend because it does not depend on Kimi WebBridge or Chrome Apple Events.
2. **Kimi WebBridge or protocol-compatible bridge**: a connected browser extension and daemon running on `KIMI_WEBBRIDGE_URL`.
3. **Chrome Apple Events**: Chrome's `View > Developer > Allow JavaScript from Apple Events` enabled. Use only when DevTools and bridge backends are unavailable.

Destination publishing requires durable values from environment variables or local config.

For `X_FEED_DESTINATION=feishu`:

- `lark-cli`.
- Lark agent skills `lark-shared`, `lark-doc`, and optionally `lark-im`.
- An authenticated Lark/Feishu session with document update and message scopes.

For `X_FEED_DESTINATION=obsidian`:

- A writable local Obsidian vault path.
- `rg` for readback verification.

Preflight:

```bash
find "${CODEX_HOME:-$HOME/.codex}/skills" "$HOME/.config/agents/skills" "$HOME/.agents/skills" \
  -maxdepth 2 -name SKILL.md 2>/dev/null | grep -E '/(kimi-webbridge|qweb-bridge|lark-doc|lark-im|lark-shared)/SKILL.md' || true

command -v lark-cli || true
command -v rg || true
curl -s --max-time 5 "${X_FEED_DEVTOOLS_URL:-http://127.0.0.1:9222}/json/version" || true
~/.kimi-webbridge/bin/kimi-webbridge status 2>/dev/null || curl -s --max-time 5 "${KIMI_WEBBRIDGE_URL:-http://127.0.0.1:10086}/status" || true
```

If no authenticated browser backend is usable, do not proceed to X. For the preferred DevTools backend, create a persistent non-default Chrome profile and ask the user to log into X once:

```bash
mkdir -p "$HOME/.chrome-profiles/x-feed-debug"
open -na "Google Chrome" --args \
  --user-data-dir="$HOME/.chrome-profiles/x-feed-debug" \
  --remote-debugging-port=9222 \
  --no-first-run \
  --no-default-browser-check \
  --new-window "https://x.com/home"
curl -s --max-time 5 "http://127.0.0.1:9222/json/version"
```

Store a launcher script path in local config when available:

```bash
X_FEED_BROWSER_BACKEND=devtools
X_FEED_DEVTOOLS_URL=http://127.0.0.1:9222
X_FEED_DEVTOOLS_PROFILE=$HOME/.chrome-profiles/x-feed-debug
X_FEED_DEVTOOLS_LAUNCHER=$HOME/.chrome-profiles/x-feed-debug/start-x-feed-debug-chrome.sh
```

Chrome 149 and newer may reject remote debugging on the default profile with `DevTools remote debugging requires a non-default data directory`; always use `--user-data-dir` for this backend.

If Kimi bridge dependencies are missing and DevTools is unavailable, offer the official installer:

```bash
curl -fsSL https://cdn.kimi.com/webbridge/install.sh | bash
```

If Feishu dependencies are missing and `X_FEED_DESTINATION=feishu`, install and configure the official Lark CLI:

```bash
npx @larksuite/cli@latest install
npx skills add larksuite/cli -g -y -a codex -s lark-shared lark-doc lark-im
lark-cli config init --new
lark-cli auth login --recommend
lark-cli auth status
```

Some commands open browser authorization pages. Surface the URL to the user and wait for them to finish authorization before continuing.

## Durable Config

Use these names:

```bash
KIMI_WEBBRIDGE_URL="${KIMI_WEBBRIDGE_URL:-http://127.0.0.1:10086}"
X_FEED_BROWSER_BACKEND="${X_FEED_BROWSER_BACKEND:-auto}"
X_FEED_DEVTOOLS_URL="${X_FEED_DEVTOOLS_URL:-http://127.0.0.1:9222}"
X_FEED_DEVTOOLS_PROFILE="${X_FEED_DEVTOOLS_PROFILE:-$HOME/.chrome-profiles/x-feed-debug}"
X_FEED_DEVTOOLS_LAUNCHER="${X_FEED_DEVTOOLS_LAUNCHER:-}"
X_FEED_STATE_FILE="${X_FEED_STATE_FILE:-$HOME/.x_feed_last_fetch}"
X_FEED_DESTINATION="${X_FEED_DESTINATION:-${CODEX_DELIVERY_DESTINATION:-feishu}}"
X_FEED_INCLUDE_FOR_YOU="${X_FEED_INCLUDE_FOR_YOU:-0}"
X_FEED_NOTIFY="${X_FEED_NOTIFY:-}"
X_FEED_PREFERENCES_FILE="${X_FEED_PREFERENCES_FILE:-$HOME/.config/x-feed-capture/preferences.md}"
LARK_DOC_TOKEN="${LARK_DOC_TOKEN:-}"
LARK_DOC_URL="${LARK_DOC_URL:-}"
LARK_DOC_ANCHOR_BLOCK_ID="${LARK_DOC_ANCHOR_BLOCK_ID:-}"
LARK_NOTIFY_CHAT_ID="${LARK_NOTIFY_CHAT_ID:-}"
OBSIDIAN_VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
OBSIDIAN_VAULT_NAME="${OBSIDIAN_VAULT_NAME:-}"
X_FEED_OBSIDIAN_SUBDIR="${X_FEED_OBSIDIAN_SUBDIR:-Clippings/X Feed Capture}"
```

Source durable config before capture:

```bash
[ -f ~/.config/codex-delivery/preferences.env ] && . ~/.config/codex-delivery/preferences.env
[ -f ~/.config/x-feed-capture/config.env ] && . ~/.config/x-feed-capture/config.env
X_FEED_DESTINATION="${X_FEED_DESTINATION:-${CODEX_DELIVERY_DESTINATION:-feishu}}"
X_FEED_BROWSER_BACKEND="${X_FEED_BROWSER_BACKEND:-auto}"
X_FEED_DEVTOOLS_URL="${X_FEED_DEVTOOLS_URL:-http://127.0.0.1:9222}"
X_FEED_DEVTOOLS_PROFILE="${X_FEED_DEVTOOLS_PROFILE:-$HOME/.chrome-profiles/x-feed-debug}"
X_FEED_DEVTOOLS_LAUNCHER="${X_FEED_DEVTOOLS_LAUNCHER:-}"
X_FEED_INCLUDE_FOR_YOU="${X_FEED_INCLUDE_FOR_YOU:-0}"
X_FEED_NOTIFY="${X_FEED_NOTIFY:-}"
X_FEED_PREFERENCES_FILE="${X_FEED_PREFERENCES_FILE:-$HOME/.config/x-feed-capture/preferences.md}"
printf 'destination=%s\nbrowser=%s\ndevtools=%s\nfor_you=%s\nnotify=%s\npreferences=%s\ndoc=%s\nurl=%s\nanchor=%s\nchat=%s\nvault=%s\n' \
  "$X_FEED_DESTINATION" \
  "$X_FEED_BROWSER_BACKEND" \
  "$X_FEED_DEVTOOLS_URL" \
  "$X_FEED_INCLUDE_FOR_YOU" \
  "${X_FEED_NOTIFY:-auto}" \
  "$X_FEED_PREFERENCES_FILE" \
  "${LARK_DOC_TOKEN:-}" \
  "${LARK_DOC_URL:-}" \
  "${LARK_DOC_ANCHOR_BLOCK_ID:-}" \
  "${LARK_NOTIFY_CHAT_ID:-}" \
  "${OBSIDIAN_VAULT_PATH:-}"
```

If `X_FEED_PREFERENCES_FILE` exists, read it during preflight and apply it as local editorial guidance. Keep the skill generic: store user-specific topic emphasis, breadth, language, and keep-policy preferences in that local file rather than editing the skill.

Notifications are optional and controlled by user preference:

- `X_FEED_NOTIFY=0` disables notifications even if `LARK_NOTIFY_CHAT_ID` is present.
- `X_FEED_NOTIFY=1` enables notifications and requires a configured notification target.
- If `X_FEED_NOTIFY` is unset, treat notifications as enabled only when a notification target such as `LARK_NOTIFY_CHAT_ID` is configured.

For Feishu publish runs, require:

- `LARK_DOC_TOKEN`
- `LARK_DOC_URL`
- `LARK_DOC_ANCHOR_BLOCK_ID`
- `LARK_NOTIFY_CHAT_ID` only when notifications are enabled

For Obsidian publish runs, require:

- `OBSIDIAN_VAULT_PATH`
- `rg`
- `LARK_NOTIFY_CHAT_ID` only when notifications are enabled through Feishu IM

If destination config is missing or required values are empty, run bootstrap first unless the user explicitly requested a dry run.

## Global Delivery Preference

To make both `x-feed-capture` and `paper-digest` use the same destination, store:

```bash
mkdir -p ~/.config/codex-delivery
cat > ~/.config/codex-delivery/preferences.env <<'EOF'
CODEX_DELIVERY_DESTINATION=obsidian
OBSIDIAN_VAULT_PATH=/absolute/path/to/vault
OBSIDIAN_VAULT_NAME=optional-vault-name
EOF
chmod 600 ~/.config/codex-delivery/preferences.env
```

Per-skill config may still override this with `X_FEED_DESTINATION=feishu` or `X_FEED_DESTINATION=obsidian`.

Set `X_FEED_INCLUDE_FOR_YOU=1` in `~/.config/x-feed-capture/config.env` to make every run include the small For You discovery sample. Leave it unset or set `0` for Following-only runs unless the user explicitly asks for For You in the prompt.

## Lark Target Bootstrap

Use the bundled helper when possible:

```bash
x-feed-capture/bin/bootstrap-x-feed-lark-targets.sh --help
```

Run it directly when enough inputs are known:

```bash
x-feed-capture/bin/bootstrap-x-feed-lark-targets.sh \
  --doc-url "https://example.feishu.cn/docx/..." \
  --anchor-text "X Feed" \
  --chat-name "AI Digest"
```

Manual acquisition:

1. Ask for the destination document URL, save it as `LARK_DOC_URL`, and extract the token from `/docx/<token>` or `/wiki/<token>`.
2. Fetch block IDs:

   ```bash
   lark-cli docs +fetch --api-version v2 \
     --doc "$LARK_DOC_TOKEN" \
     --detail with-ids
   ```

3. Choose a stable insertion anchor near the top, such as `X Feed` or `Latest Captures`, and record its block ID as `LARK_DOC_ANCHOR_BLOCK_ID`.
4. Locate the notification chat:

   ```bash
   lark-cli im +chat-search --as user --query "chat name"
   ```

5. Store config with file mode `600`:

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

Do not store these values in cache, automation memory markdown, or the skill repository.

## Obsidian Target Bootstrap

No API bootstrap is required. Verify the vault path and store it in either the global delivery preference or this skill's config:

```bash
test -d "$OBSIDIAN_VAULT_PATH/.obsidian" || test -d "$OBSIDIAN_VAULT_PATH"
mkdir -p ~/.config/x-feed-capture
cat >> ~/.config/x-feed-capture/config.env <<'EOF'
X_FEED_DESTINATION=obsidian
X_FEED_NOTIFY=0
OBSIDIAN_VAULT_PATH=/absolute/path/to/vault
OBSIDIAN_VAULT_NAME=optional-vault-name
X_FEED_OBSIDIAN_SUBDIR=Clippings/X Feed Capture
X_FEED_PREFERENCES_FILE=$HOME/.config/x-feed-capture/preferences.md
EOF
chmod 600 ~/.config/x-feed-capture/config.env
```
