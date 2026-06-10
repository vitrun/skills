# Paper Digest Setup

## Dependencies

Digest generation works with the bundled public AlphaXiv fetcher:

```bash
python3 paper-digest/scripts/fetch-alphaxiv-hot.py --help
```

Publishing and notification require:

- `lark-cli`.
- Lark agent skills `lark-shared` and `lark-doc`.
- Lark agent skill `lark-im` when notification is enabled.
- An authenticated Lark/Feishu session with document-update and message-send scopes.
- `jq` and `perl` for the bundled one-time Lark target bootstrap helper.

Before publishing:

```bash
command -v lark-cli || true
find "${CODEX_HOME:-$HOME/.codex}/skills" "$HOME/.config/agents/skills" "$HOME/.agents/skills" \
  -maxdepth 2 -name SKILL.md 2>/dev/null | grep -E '/(lark-shared|lark-doc|lark-im)/SKILL.md' || true
lark-cli auth status 2>/dev/null || true
```

If Lark dependencies are missing and the user wants publishing:

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
PAPER_DIGEST_CONFIG="${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}"
[ -f "$PAPER_DIGEST_CONFIG" ] && . "$PAPER_DIGEST_CONFIG"
```

Variables:

```bash
PAPER_DIGEST_FETCH_SCRIPT="${PAPER_DIGEST_FETCH_SCRIPT:-paper-digest/scripts/fetch-alphaxiv-hot.py}"
PAPER_DIGEST_DOC_TOKEN="${PAPER_DIGEST_DOC_TOKEN:-}"
PAPER_DIGEST_DOC_URL="${PAPER_DIGEST_DOC_URL:-}"
PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID="${PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID:-}"
PAPER_DIGEST_DOC_AS="${PAPER_DIGEST_DOC_AS:-user}"
PAPER_DIGEST_NOTIFY_CHAT_ID="${PAPER_DIGEST_NOTIFY_CHAT_ID:-}"
PAPER_DIGEST_NOTIFY_AS="${PAPER_DIGEST_NOTIFY_AS:-user}"
PAPER_DIGEST_CACHE_DIR="${PAPER_DIGEST_CACHE_DIR:-$HOME/.cache/paper-digest}"
```

Do not depend on private runner paths. If `PAPER_DIGEST_FETCH_SCRIPT` is unset, resolve the bundled fetcher relative to this skill folder. A custom fetcher is allowed only when explicitly configured; it should fetch and format content, not publish to private defaults.

For publish, scheduled, or automation runs, require:

- `PAPER_DIGEST_DOC_TOKEN`
- `PAPER_DIGEST_DOC_URL`
- `PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID`
- `PAPER_DIGEST_NOTIFY_CHAT_ID`, unless the user explicitly says to skip notification

If any required value is missing, bootstrap first unless the user explicitly asks for dry run.

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
