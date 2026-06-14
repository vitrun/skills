# Paper Digest Setup

## Dependencies

Digest generation works with the bundled public AlphaXiv fetcher:

```bash
python3 paper-digest/scripts/fetch-alphaxiv-hot.py --help
```

Destination publishing requires durable values from environment variables or local config.

For `PAPER_DIGEST_DESTINATION=feishu`:

- `lark-cli`.
- Lark agent skills `lark-shared` and `lark-doc`.
- Lark agent skill `lark-im` when notification is enabled.
- An authenticated Lark/Feishu session with document-update and message-send scopes.
- `jq` and `perl` for the bundled one-time Lark target bootstrap helper.

For `PAPER_DIGEST_DESTINATION=obsidian`:

- A writable local Obsidian vault path.
- `rg` for readback verification.
- `jq` when verifying arXiv links from `preview.json`.

Before publishing, run the checks relevant to the selected destination:

```bash
command -v lark-cli || true
command -v rg || true
command -v jq || true
find "${CODEX_HOME:-$HOME/.codex}/skills" "$HOME/.config/agents/skills" "$HOME/.agents/skills" \
  -maxdepth 2 -name SKILL.md 2>/dev/null | grep -E '/(lark-shared|lark-doc|lark-im)/SKILL.md' || true
lark-cli auth status 2>/dev/null || true
```

If Feishu dependencies are missing and `PAPER_DIGEST_DESTINATION=feishu`:

```bash
npx @larksuite/cli@latest install
npx skills add larksuite/cli -g -y -a codex -s lark-shared lark-doc lark-im
lark-cli config init --new
lark-cli auth login --recommend
lark-cli auth status
```

Some commands open browser authorization pages. Surface the URL and wait for authorization before continuing.

## Durable Config

Source durable config before reading variables:

```bash
[ -f "$HOME/.config/codex-delivery/preferences.env" ] && . "$HOME/.config/codex-delivery/preferences.env"
PAPER_DIGEST_CONFIG="${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}"
[ -f "$PAPER_DIGEST_CONFIG" ] && . "$PAPER_DIGEST_CONFIG"
PAPER_DIGEST_DESTINATION="${PAPER_DIGEST_DESTINATION:-${CODEX_DELIVERY_DESTINATION:-feishu}}"
```

Variables:

```bash
PAPER_DIGEST_FETCH_SCRIPT="${PAPER_DIGEST_FETCH_SCRIPT:-paper-digest/scripts/fetch-alphaxiv-hot.py}"
PAPER_DIGEST_PREFERENCES_FILE="${PAPER_DIGEST_PREFERENCES_FILE:-$HOME/.config/paper-digest/preferences.json}"
PAPER_DIGEST_DESTINATION="${PAPER_DIGEST_DESTINATION:-${CODEX_DELIVERY_DESTINATION:-feishu}}"
PAPER_DIGEST_DOC_TOKEN="${PAPER_DIGEST_DOC_TOKEN:-}"
PAPER_DIGEST_DOC_URL="${PAPER_DIGEST_DOC_URL:-}"
PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID="${PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID:-}"
PAPER_DIGEST_DOC_AS="${PAPER_DIGEST_DOC_AS:-user}"
PAPER_DIGEST_NOTIFY_CHAT_ID="${PAPER_DIGEST_NOTIFY_CHAT_ID:-}"
PAPER_DIGEST_NOTIFY_AS="${PAPER_DIGEST_NOTIFY_AS:-user}"
PAPER_DIGEST_CACHE_DIR="${PAPER_DIGEST_CACHE_DIR:-$HOME/.cache/paper-digest}"
OBSIDIAN_VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
OBSIDIAN_VAULT_NAME="${OBSIDIAN_VAULT_NAME:-}"
PAPER_DIGEST_OBSIDIAN_SUBDIR="${PAPER_DIGEST_OBSIDIAN_SUBDIR:-Papers/Digests}"
PAPER_DIGEST_OBSIDIAN_FILE="${PAPER_DIGEST_OBSIDIAN_FILE:-}"
```

Do not depend on private runner paths. If `PAPER_DIGEST_FETCH_SCRIPT` is unset, resolve the bundled fetcher relative to this skill folder. A custom fetcher is allowed only when explicitly configured; it should fetch and format content, not publish to private defaults.

If `PAPER_DIGEST_PREFERENCES_FILE` exists, the agent should read it and use its
`interested` and `excluded` free-text lists during curation. Copy
[`paper-digest/assets/preferences.example.json`](../assets/preferences.example.json)
to bootstrap the file.

For Feishu publish, scheduled, or automation runs, require:

- `PAPER_DIGEST_DOC_TOKEN`
- `PAPER_DIGEST_DOC_URL`
- `PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID`
- `PAPER_DIGEST_NOTIFY_CHAT_ID`, unless the user explicitly says to skip notification

For Obsidian publish, scheduled, or automation runs, require:

- `OBSIDIAN_VAULT_PATH`
- `rg`
- `PAPER_DIGEST_NOTIFY_CHAT_ID` only if notifications are still configured through Feishu IM

If `PAPER_DIGEST_OBSIDIAN_FILE` is unset, the default publish target is one monthly note named `YYYY-MM Paper Digest.md`, with each new digest prepended near the top.

If any required destination value is missing, bootstrap first unless the user explicitly asks for dry run.

## Global Delivery Preference

To make both `paper-digest` and `x-feed-capture` use the same destination, store:

```bash
mkdir -p ~/.config/codex-delivery
cat > ~/.config/codex-delivery/preferences.env <<'EOF'
CODEX_DELIVERY_DESTINATION=obsidian
OBSIDIAN_VAULT_PATH=/absolute/path/to/vault
OBSIDIAN_VAULT_NAME=optional-vault-name
EOF
chmod 600 ~/.config/codex-delivery/preferences.env
```

Per-skill config may still override this with `PAPER_DIGEST_DESTINATION=feishu` or `PAPER_DIGEST_DESTINATION=obsidian`.

## Lark Target Bootstrap

Use:

```bash
paper-digest/bin/bootstrap-paper-digest-lark-targets.sh --help
```

Run directly when enough inputs are known:

```bash
paper-digest/bin/bootstrap-paper-digest-lark-targets.sh \
  --doc-url "https://example.feishu.cn/docx/..." \
  --anchor-text "Paper Digest" \
  --chat-name "AI Digest"
```

```bash
paper-digest/bin/bootstrap-paper-digest-lark-targets.sh \
  --create-doc \
  --doc-title "Paper Digest" \
  --skip-chat
```

The helper:

- extracts a doc token from an existing docx/wiki URL or creates a new doc;
- stores the destination document URL for notifications;
- fetches block IDs and resolves a stable insertion anchor;
- searches a notify chat by name or accepts an explicit `oc_...` chat ID;
- writes `~/.config/paper-digest/config.env` with file mode `600`;
- stores the bundled fetch script path so automations do not depend on workspace-local private scripts.

Store durable config in `~/.config/paper-digest/config.env`, not in cache, automation memory, the skill repository, or generated digest files.

## Obsidian Target Bootstrap

No API bootstrap is required. Verify the vault path and store it in either the global delivery preference or this skill's config:

```bash
test -d "$OBSIDIAN_VAULT_PATH/.obsidian" || test -d "$OBSIDIAN_VAULT_PATH"
mkdir -p ~/.config/paper-digest
cat >> ~/.config/paper-digest/config.env <<'EOF'
PAPER_DIGEST_DESTINATION=obsidian
OBSIDIAN_VAULT_PATH=/absolute/path/to/vault
OBSIDIAN_VAULT_NAME=optional-vault-name
PAPER_DIGEST_OBSIDIAN_SUBDIR=Papers/Digests
EOF
chmod 600 ~/.config/paper-digest/config.env
```
