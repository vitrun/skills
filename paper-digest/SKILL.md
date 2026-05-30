---
name: paper-digest
description: Fetch recent AI/ML papers, deduplicate and filter them, format a concise paper digest, publish it to a Lark/Feishu document when requested, and notify the result on success, no-op, or failure. Use when the user asks for a paper digest, AlphaXiv hot papers, recent AI research summaries, or publishing a research-paper roundup.
---

# Paper Digest

## Overview

Produce a concise AI paper digest from the bundled AlphaXiv fetcher or another explicitly configured fetcher, then optionally insert it into a configured Lark/Feishu document. For publish or scheduled/automation runs, always send a completion notification whether the run succeeds, produces no updates, or fails.

Do not hardcode or commit private document tokens, chat IDs, Feishu/Lark URLs, local usernames, cache contents, or API credentials. Read them from environment variables, local config, or the user's explicit prompt.

## Dependencies

Digest generation works with the bundled public AlphaXiv fetcher:

```bash
python3 paper-digest/scripts/fetch-alphaxiv-hot.py --help
```

Publishing and notification require Lark/Feishu tooling.

Required for publishing:

- `lark-cli`.
- Lark agent skills `lark-shared` and `lark-doc`.
- Lark agent skill `lark-im` when notification is enabled.
- An authenticated Lark/Feishu session with document-update and message-send scopes when publishing with notification.
- `jq` and `perl` for the bundled one-time Lark target bootstrap helper.

Before publishing, check:

```bash
command -v lark-cli || true
find "${CODEX_HOME:-$HOME/.codex}/skills" "$HOME/.config/agents/skills" "$HOME/.agents/skills" \
  -maxdepth 2 -name SKILL.md 2>/dev/null | grep -E '/(lark-shared|lark-doc|lark-im)/SKILL.md' || true
lark-cli auth status 2>/dev/null || true
```

If Lark dependencies are missing and the user wants publishing, offer to install and authenticate the official CLI:

```bash
npx @larksuite/cli@latest install
npx skills add larksuite/cli -g -y -a codex -s lark-shared lark-doc lark-im
lark-cli config init --new
lark-cli auth login --recommend
lark-cli auth status
```

Some commands open browser authorization pages. Surface the URL to the user and wait for them to finish authorization before continuing.

## Configuration

Source durable local config before reading individual variables:

```bash
PAPER_DIGEST_CONFIG="${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}"
[ -f "$PAPER_DIGEST_CONFIG" ] && . "$PAPER_DIGEST_CONFIG"
```

Use these variables:

```bash
PAPER_DIGEST_FETCH_SCRIPT="${PAPER_DIGEST_FETCH_SCRIPT:-paper-digest/scripts/fetch-alphaxiv-hot.py}"
PAPER_DIGEST_DOC_TOKEN="${PAPER_DIGEST_DOC_TOKEN:-}"
PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID="${PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID:-}"
PAPER_DIGEST_DOC_AS="${PAPER_DIGEST_DOC_AS:-user}"
PAPER_DIGEST_NOTIFY_CHAT_ID="${PAPER_DIGEST_NOTIFY_CHAT_ID:-}"
PAPER_DIGEST_NOTIFY_AS="${PAPER_DIGEST_NOTIFY_AS:-user}"
PAPER_DIGEST_CACHE_DIR="${PAPER_DIGEST_CACHE_DIR:-$HOME/.cache/paper-digest}"
```

Do not depend on `~/tasks`, `/Users/.../Work/tasks`, or any private runner. If `PAPER_DIGEST_FETCH_SCRIPT` is unset, resolve the bundled `scripts/fetch-alphaxiv-hot.py` relative to this skill folder. A custom fetcher is allowed only when explicitly configured; it should fetch and format content, not publish to private defaults.

For publish, scheduled, or automation runs, require:

- `PAPER_DIGEST_DOC_TOKEN`
- `PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID`
- `PAPER_DIGEST_NOTIFY_CHAT_ID`, unless the user explicitly says to skip notification

If any required value is missing, do not silently generate a local-only digest and call it done. Treat this as an onboarding gap and guide the user through the Lark target bootstrap first. Only fall back to local dry-run behavior if the user explicitly asks for a dry run or declines bootstrap.

### Lark target bootstrap

When publishing is requested and `PAPER_DIGEST_DOC_TOKEN`, `PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID`, or `PAPER_DIGEST_NOTIFY_CHAT_ID` is missing, use the bundled helper to acquire and persist the values:

```bash
paper-digest/bin/bootstrap-paper-digest-lark-targets.sh --help
```

Run the helper directly when the prompt or local context already provides enough input. Examples:

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
- fetches the document with block IDs and resolves a stable insertion anchor;
- searches a notify chat by name or accepts an explicit `oc_...` chat ID;
- writes `~/.config/paper-digest/config.env` with file mode `600`;
- stores the bundled fetch script path so automations do not depend on workspace-local private scripts.

Manual acquisition flow when not using the helper:

1. **Document token**
   - Ask for the destination document URL and extract the token from `/docx/<token>` or `/wiki/<token>`.
   - If needed, create a destination with `lark-cli docs +create --api-version v2`.

2. **Anchor block ID**
   - Fetch block IDs:

   ```bash
   lark-cli docs +fetch --api-version v2 \
     --as "${PAPER_DIGEST_DOC_AS:-user}" \
     --doc "$PAPER_DIGEST_DOC_TOKEN" \
     --detail with-ids
   ```

   - Use a stable heading near the top, such as `Paper Digest`, and record its `id="..."` as `PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID`.

3. **Notify chat ID**
   - If notifications are desired, search the chat:

   ```bash
   lark-cli im +chat-search --as user --query "chat name"
   ```

   - Record the returned `chat_id` (`oc_...`) as `PAPER_DIGEST_NOTIFY_CHAT_ID`.

Store durable config in `~/.config/paper-digest/config.env`, not in `~/.cache`, automation memory, the skill repository, or generated digest files:

```bash
mkdir -p ~/.config/paper-digest
cat > ~/.config/paper-digest/config.env <<'EOF'
PAPER_DIGEST_FETCH_SCRIPT=/path/to/paper-digest/scripts/fetch-alphaxiv-hot.py
PAPER_DIGEST_DOC_TOKEN=doxcnxxxxxxxxxxxx
PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID=blkcnxxxxxxxxxxxx
PAPER_DIGEST_DOC_AS=user
PAPER_DIGEST_NOTIFY_CHAT_ID=oc_xxxxxxxxxxxx
PAPER_DIGEST_NOTIFY_AS=user
EOF
chmod 600 ~/.config/paper-digest/config.env
```

## Workflow

### 1. Run preflight and load config

Before fetching papers, load durable config and check whether this run is supposed to publish:

```bash
PAPER_DIGEST_CONFIG="${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}"
[ -f "$PAPER_DIGEST_CONFIG" ] && . "$PAPER_DIGEST_CONFIG"
printf 'fetch=%s\ndoc=%s\nanchor=%s\nchat=%s\n' \
  "${PAPER_DIGEST_FETCH_SCRIPT:-}" \
  "${PAPER_DIGEST_DOC_TOKEN:-}" \
  "${PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID:-}" \
  "${PAPER_DIGEST_NOTIFY_CHAT_ID:-}"
```

If publishing or automation is intended and the config file or required variables are missing, pause the workflow and run the bootstrap helper first unless the user explicitly asked for dry-run behavior.

Resolve the fetcher:

```bash
PAPER_DIGEST_FETCH_SCRIPT="${PAPER_DIGEST_FETCH_SCRIPT:-paper-digest/scripts/fetch-alphaxiv-hot.py}"
python3 "$PAPER_DIGEST_FETCH_SCRIPT" --help
```

The bundled fetcher supports `--limit`, `--interval`, `--sort`, `--output md|json`, `--cache-dir`, `--no-cache`, `--no-cache-write`, and `--no-filter`.

### 2. Run a dry preview first

Produce a structured preview before publishing:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --cache-dir "$PAPER_DIGEST_CACHE_DIR" \
  --no-cache-write \
  --output json > preview.json
```

Then generate Markdown for the publish candidate:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --cache-dir "$PAPER_DIGEST_CACHE_DIR" \
  --no-cache-write \
  --output md > digest.md
```

Check that papers are new, relevant, and not obviously outside the requested scope. Do not use compact output; preserve enough detail for useful evaluation.

If `preview.json` has `filtered_count == 0`, skip document publishing and send the no-updates notification. Do not insert a "no new papers" digest into the document unless the user explicitly asks for that audit trail.

For publish runs, keep the JSON preview as `preview.json` and only mark papers as seen after the document update succeeds:

```bash
mkdir -p "$PAPER_DIGEST_CACHE_DIR"
jq -r '.papers[].arxiv_id // empty' preview.json >> "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt"
sort -u "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt" -o "$PAPER_DIGEST_CACHE_DIR/seen_ids.txt"
```

### 3. Filter and deduplicate

Keep AI/ML papers with useful research or product relevance. Prefer LLMs, agents, multimodal models, developer tooling, evaluation, data, inference, infrastructure, and applied AI systems.

Filter out papers that are outside the requested focus, duplicates from the local cache, or low-value for the digest audience. Use the local cache directory when available, but do not commit cache files.

### 4. Format the digest

Use this Markdown heading structure exactly when the digest will be published to a document:

- The date/run title is the only H2: `## YYYY-MM-DD Paper Digest`.
- Each paper title is H3: `### <paper title>`.
- Do not use H2 for paper titles.
- Keep per-paper details as bullets under the H3. If a nested label is needed, use bold text inside bullets such as `- **Method:** ...`, not another heading.

For each paper, include:

- Title.
- arXiv link and, when available, AlphaXiv link.
- Authors or institutions when useful.
- One or two bullets for the core problem.
- One or two bullets for the method.
- One or two bullets for key insight or result.

Keep bullets short and concrete. Avoid copying large abstracts verbatim.

Before publishing Markdown, normalize and validate heading levels:

```bash
# Expected: exactly one line, the date/run title.
rg -n '^## ' digest.md

# Expected: one H3 per paper.
rg -n '^### ' digest.md
```

If a runner emits paper titles as `##`, rewrite those paper title headings to `###` before inserting into the document. Do not publish Markdown where `^## ` matches anything other than the date/run title.

### 5. Publish only with explicit targets

When the user asks to publish, or this is a scheduled/automation run, require configured document and anchor targets:

```bash
: "${PAPER_DIGEST_DOC_TOKEN:?set destination document token}"
: "${PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID:?set destination anchor block id}"
```

Also require `PAPER_DIGEST_NOTIFY_CHAT_ID` unless the user explicitly says to skip notification.

Insert the Markdown digest after the configured anchor block with `lark-cli docs +update`. Use a relative `@digest.md` path from the directory that contains the file; `lark-cli` rejects absolute `@/tmp/...` content paths.

```bash
(cd "$(dirname "$DIGEST_PATH")" && \
  lark-cli docs +update --api-version v2 \
    --as "${PAPER_DIGEST_DOC_AS:-user}" \
    --doc "$PAPER_DIGEST_DOC_TOKEN" \
    --command block_insert_after \
    --block-id "$PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID" \
    --doc-format markdown \
    --content @"$(basename "$DIGEST_PATH")" > publish.json)
jq -e '.ok == true' "$(dirname "$DIGEST_PATH")/publish.json" >/dev/null
```

After this command succeeds, mark the published IDs as seen using the `preview.json` command from step 2. Do not update the dedupe cache before a successful publish.

Do not rely on `lark-cli` exit code alone. Some validation failures are returned as JSON with `"ok": false` while the process exits successfully, so always inspect `.ok == true` before marking papers as seen or sending a success notification.

Never rely on a fetcher's hardcoded document defaults. Publishing belongs in this workflow, not in the fetch script.

For automation, wrap publish and notify in a small shell function or script so the original failure is retained and notification is attempted in all terminal outcomes.

### 6. Notify completion in all outcomes

For any publish, scheduled, or automation run, send a concise notification after the run finishes. This is mandatory for all terminal outcomes:

- Success: number of fetched, filtered, and published papers.
- No updates: state that no new papers matched after deduplication/filtering.
- Failure: failing step plus the command, missing config key, or permission the user should check.

Use `lark-im` / `lark-cli im +messages-send` with `--chat-id "$PAPER_DIGEST_NOTIFY_CHAT_ID"` and `--as "${PAPER_DIGEST_NOTIFY_AS:-user}"`. Prefer `--text` for exact status text. Treat a configured notification chat plus an explicit user request to run/publish this workflow as approval to send the concise status message; if the destination, content class, or sending identity is unclear, ask once before the first send.

```bash
lark-cli im +messages-send \
  --as "${PAPER_DIGEST_NOTIFY_AS:-user}" \
  --chat-id "$PAPER_DIGEST_NOTIFY_CHAT_ID" \
  --text "Paper Digest: success
Window: 7 Days
Published: 5
Destination: configured Feishu doc"
```

Implement the workflow with `try/finally`, shell `trap`, or equivalent control flow so notification is attempted even after fetch, filter, format, or publish failures. Capture the original failure first; if notification also fails, report both the original failure and the notification failure locally.

Notification content must not include private document tokens, raw access tokens, app secrets, full local paths, or personal identifiers. Prefer this shape:

```text
Paper Digest: success
Window: 7 Days
Fetched: 20
Published: 16
Destination: configured Feishu doc
```

```text
Paper Digest: failed
Step: publish
Reason: missing PAPER_DIGEST_DOC_TOKEN
Action: run bin/bootstrap-paper-digest-lark-targets.sh and rerun
```

## Public Repo Hygiene

- Do not include real Feishu/Lark document URLs or tokens in this skill.
- Do not include personal filesystem paths or usernames.
- Do not copy private local runner scripts into the public skill unless they have been audited and stripped of defaults, tokens, private URLs, and cache paths.
- Keep generated output, cache files, and raw fetched data out of the `skills` repository.
