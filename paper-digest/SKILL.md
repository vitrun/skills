---
name: paper-digest
description: Fetch recent AI/ML papers, deduplicate and filter them, format a concise paper digest, publish it to a Lark/Feishu document when requested, and notify the result on success, no-op, or failure. Use when the user asks for a paper digest, AlphaXiv hot papers, recent AI research summaries, or publishing a research-paper roundup.
---

# Paper Digest

Produce a concise AI paper digest from the bundled AlphaXiv fetcher or an explicitly configured fetcher, then optionally insert it into a configured Lark/Feishu document. For publish or scheduled runs, always send a completion notification whether the run succeeds, produces no updates, or fails.

Do not hardcode or commit private document tokens, chat IDs, Feishu/Lark URLs, local usernames, cache contents, or API credentials.

## Resource Map

- Read [references/setup.md](references/setup.md) for dependencies, config, and Lark bootstrap.
- Read [references/workflow.md](references/workflow.md) for fetch, preview, dedupe, publish, notify, and cache-update details.
- Read [references/formatting.md](references/formatting.md) before publishing Markdown to a document.
- Read [references/gotchas.md](references/gotchas.md) when publish, notification, cache, or CLI behavior is surprising.
- Use [assets/digest-template.md](assets/digest-template.md) as the digest shape.
- Use [scripts/fetch-alphaxiv-hot.py](scripts/fetch-alphaxiv-hot.py) as the default public fetcher.
- Prefer [bin/bootstrap-paper-digest-lark-targets.sh](bin/bootstrap-paper-digest-lark-targets.sh) for first-run publish setup.

## Non-Negotiables

- Load durable config before deciding whether this is a publish run.
- For publish, scheduled, or automation runs, require destination doc URL, token, anchor, and notification chat unless the user explicitly skips notification.
- If required publish config is missing, bootstrap first. Do not silently generate a local-only digest and call it done.
- Run a structured preview before publishing.
- Mark papers as seen only after document publish succeeds.
- Inspect publish JSON for `.ok == true`; do not rely on process exit code alone.
- Notify success, no-update, or failure for every publish/scheduled run.

## Workflow

1. **Preflight and config**
   - Source `${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}` if present.
   - Verify the fetcher and Lark dependencies when publishing. See [references/setup.md](references/setup.md).

2. **Preview**
   - Run the fetcher with `--output json` and `--no-cache-write`.
   - Run the fetcher with `--output md` and `--no-cache-write`.
   - Preserve both artifacts for validation and reporting.

3. **Filter and format**
   - Keep useful AI/ML papers with research or product relevance.
   - Filter duplicates via the configured cache directory.
   - Validate heading levels before publishing. See [references/formatting.md](references/formatting.md).

4. **Publish**
   - Insert the Markdown digest after `PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID`.
   - Use a relative `@digest.md` content path from the digest directory.
   - Confirm `.ok == true`. See [references/workflow.md](references/workflow.md).

5. **Update dedupe state**
   - Append published paper IDs to `seen_ids.txt` only after publish success.
   - Sort and deduplicate the cache file.

6. **Notify**
   - Send concise success, no-update, or failure status.
   - Include `Document: $PAPER_DIGEST_DOC_URL`.

## Final Report

Report:

- fetched, filtered, and published counts
- artifact paths
- publish/notification result
- cache update result
- recovered errors and remaining follow-up
