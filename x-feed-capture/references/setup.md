# X Feed Capture Setup

## Dependencies

Capture requires:

- Kimi WebBridge or a protocol-compatible local bridge running on `KIMI_WEBBRIDGE_URL`.
- A browser extension connected to that bridge and logged into X in the user's normal browser profile.
- An agent skill or local documentation for the bridge, such as `kimi-webbridge` or `qweb-bridge`.

Publishing requires:

- `lark-cli`.
- Lark agent skills `lark-shared`, `lark-doc`, and optionally `lark-im`.
- An authenticated Lark/Feishu session with document update and message scopes.
- Durable destination values from environment variables or local config.

Preflight:

```bash
find "${CODEX_HOME:-$HOME/.codex}/skills" "$HOME/.config/agents/skills" "$HOME/.agents/skills" \
  -maxdepth 2 -name SKILL.md 2>/dev/null | grep -E '/(kimi-webbridge|qweb-bridge|lark-doc|lark-im|lark-shared)/SKILL.md' || true

command -v lark-cli || true
~/.kimi-webbridge/bin/kimi-webbridge status 2>/dev/null || curl -s --max-time 5 "${KIMI_WEBBRIDGE_URL:-http://127.0.0.1:10086}/status" || true
```

If bridge dependencies are missing, do not proceed to X. Offer the official installer:

```bash
curl -fsSL https://cdn.kimi.com/webbridge/install.sh | bash
```

If Lark dependencies are missing and publishing is requested, install and configure the official Lark CLI:

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
X_FEED_STATE_FILE="${X_FEED_STATE_FILE:-$HOME/.x_feed_last_fetch}"
LARK_DOC_TOKEN="${LARK_DOC_TOKEN:-}"
LARK_DOC_URL="${LARK_DOC_URL:-}"
LARK_DOC_ANCHOR_BLOCK_ID="${LARK_DOC_ANCHOR_BLOCK_ID:-}"
LARK_NOTIFY_CHAT_ID="${LARK_NOTIFY_CHAT_ID:-}"
```

Source durable config before capture:

```bash
[ -f ~/.config/x-feed-capture/config.env ] && . ~/.config/x-feed-capture/config.env
printf 'doc=%s\nurl=%s\nanchor=%s\nchat=%s\n' "${LARK_DOC_TOKEN:-}" "${LARK_DOC_URL:-}" "${LARK_DOC_ANCHOR_BLOCK_ID:-}" "${LARK_NOTIFY_CHAT_ID:-}"
```

For publish runs, require:

- `LARK_DOC_TOKEN`
- `LARK_DOC_URL`
- `LARK_DOC_ANCHOR_BLOCK_ID`
- `LARK_NOTIFY_CHAT_ID`, unless the user explicitly says to skip notification

If the config file is missing or required values are empty, run bootstrap first unless the user explicitly requested a dry run.

## Lark Target Bootstrap

Use the bundled helper when possible:

```bash
/Users/axel/Work/skills/x-feed-capture/bin/bootstrap-x-feed-lark-targets.sh --help
```

Run it directly when enough inputs are known:

```bash
/Users/axel/Work/skills/x-feed-capture/bin/bootstrap-x-feed-lark-targets.sh \
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
