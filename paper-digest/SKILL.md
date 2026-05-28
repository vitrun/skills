---
name: paper-digest
description: Fetch recent AI/ML papers, deduplicate and filter them, format a concise paper digest, publish it to a Lark/Feishu document when requested, and notify the result on success, no-op, or failure. Use when the user asks for a paper digest, AlphaXiv hot papers, recent AI research summaries, or publishing a research-paper roundup.
---

# Paper Digest

## Overview

Produce a concise AI paper digest from a configured local fetcher or public paper source, then optionally insert it into a configured document. For publish or scheduled/automation runs, always send a completion notification whether the run succeeds, produces no updates, or fails.

Do not hardcode or commit private document tokens, chat IDs, Feishu/Lark URLs, local usernames, cache contents, or API credentials. Read them from environment variables, local config, or the user's explicit prompt.

## Dependencies

Digest generation can run from a local script or public paper source. Publishing and notification require Lark/Feishu tooling.

Required for publishing:

- `lark-cli`.
- Lark agent skills `lark-shared` and `lark-doc`.
- Lark agent skill `lark-im` when notification is enabled.
- An authenticated Lark/Feishu session with document-update and message-send scopes when publishing with notification.

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

Prefer these environment variables:

```bash
PAPER_DIGEST_FETCH_SCRIPT="${PAPER_DIGEST_FETCH_SCRIPT:-}"
PAPER_DIGEST_DOC_TOKEN="${PAPER_DIGEST_DOC_TOKEN:-}"
PAPER_DIGEST_NOTIFY_CHAT_ID="${PAPER_DIGEST_NOTIFY_CHAT_ID:-}"
PAPER_DIGEST_NOTIFY_AS="${PAPER_DIGEST_NOTIFY_AS:-bot}"
PAPER_DIGEST_CACHE_DIR="${PAPER_DIGEST_CACHE_DIR:-$HOME/.cache/paper-digest}"
```

If `PAPER_DIGEST_FETCH_SCRIPT` is not set, look for an obvious local runner such as `tasks/paper-digest-fetch.py` in the current workspace. If no runner exists, fetch from a public source such as AlphaXiv directly or ask the user for the intended script.

Never rely on a runner's hardcoded private defaults. Pass document and notification targets explicitly when publishing.

For publish, scheduled, or automation runs, require `PAPER_DIGEST_NOTIFY_CHAT_ID` unless the user explicitly says to skip notification. If it is missing, fail before publishing and report the missing configuration locally instead of silently running without a notification path.

## Workflow

### 1. Inspect the runner

If using a local script, inspect its help before running because option names vary:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" --help
```

Map the available flags to the requested operation. Common options include:

- `--limit 20` for the maximum number of papers.
- `--interval "7 Days"` or `--interval "1 Day"` for the time window.
- `--no-cache` to bypass deduplication for debugging.
- `--no-filter` to bypass topic filtering for debugging.
- `--output json` to inspect structured output.
- `--doc` or `--doc-token` to provide the destination document token.
- `--insert` or omitting `--dry` to publish, depending on the runner.

Do not use a compact mode if the runner provides one; preserve enough detail for useful evaluation.

### 2. Run a dry preview first

For local scripts, produce a preview before publishing:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --output json
```

If the runner uses `--dry` for Markdown previews, prefer that for human review. Check that papers are new, relevant, and not obviously outside the requested scope.

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

When the user asks to publish, require configured document and notification targets:

```bash
: "${PAPER_DIGEST_DOC_TOKEN:?set destination document token}"
: "${PAPER_DIGEST_NOTIFY_CHAT_ID:?set notification chat id}"
```

Then run the local script with explicit destination flags. Examples:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --doc "$PAPER_DIGEST_DOC_TOKEN"
```

or, for runners that use different names:

```bash
python3 "$PAPER_DIGEST_FETCH_SCRIPT" \
  --limit 20 \
  --interval "7 Days" \
  --doc-token "$PAPER_DIGEST_DOC_TOKEN" \
  --insert
```

Choose the variant supported by `--help`; do not pass unsupported flags.

### 6. Notify completion in all outcomes

For any publish, scheduled, or automation run, send a concise notification after the run finishes. This is mandatory for all terminal outcomes:

- Success: number of fetched, filtered, and published papers.
- No updates: state that no new papers matched after deduplication/filtering.
- Failure: failing step plus the command, missing config key, or permission the user should check.

Use `lark-im` / `lark-cli im +messages-send` with `--chat-id "$PAPER_DIGEST_NOTIFY_CHAT_ID"` and `--as "${PAPER_DIGEST_NOTIFY_AS:-bot}"`. Prefer `--text` for exact status text. Treat a configured notification chat plus an explicit user request to run/publish this workflow as approval to send the concise status message; if the destination, content class, or sending identity is unclear, ask once before the first send.

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
Action: configure the destination doc token and rerun
```

## Public Repo Hygiene

- Do not include real Feishu/Lark document URLs or tokens in this skill.
- Do not include personal filesystem paths or usernames.
- Do not copy private local runner scripts into the public skill unless they have been audited and stripped of defaults, tokens, private URLs, and cache paths.
- Keep generated output, cache files, and raw fetched data out of the `skills` repository.
