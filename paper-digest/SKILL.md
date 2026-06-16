---
name: paper-digest
description: Fetch, deduplicate, curate, publish, and notify recent AI/ML paper roundups using agent-level preferences and configured destinations such as Lark/Feishu or Obsidian. Use when the user asks for a paper digest, AlphaXiv hot papers, recent AI research summaries, or a published research-paper roundup. Do not use for single-paper lookup or OKF-style pattern libraries.
---

# Paper Digest

Produce a concise AI paper digest from the bundled AlphaXiv fetcher or an explicitly configured fetcher, then optionally publish it to the configured destination. For publish or scheduled runs, always send a completion notification whether the run succeeds, produces no updates, or fails.

Do not hardcode or commit private document tokens, chat IDs, Feishu/Lark URLs, local usernames, cache contents, or API credentials.

## Resource Map

- Read [references/setup.md](references/setup.md) for dependencies, config, destination preference, and one-time setup.
- Read [references/workflow.md](references/workflow.md) for fetch, preview, dedupe, destination publish, notify, and cache-update details.
- Read [references/preferences.md](references/preferences.md) for the interested/excluded preference model and curation contract.
- Read [references/destinations.md](references/destinations.md) before publishing, notifying, or updating dedupe state.
- Read [references/obsidian-publish.md](references/obsidian-publish.md) for the Obsidian destination.
- Read [references/formatting.md](references/formatting.md) before publishing Markdown to a document.
- Read [references/gotchas.md](references/gotchas.md) when publish, notification, cache, or CLI behavior is surprising.
- Use [assets/digest-template.md](assets/digest-template.md) as the digest shape.
- Use [assets/preferences.example.json](assets/preferences.example.json) as the preference file shape.
- Use [assets/selection-template.json](assets/selection-template.json) as the curation handoff shape.
- Use [scripts/fetch-alphaxiv-hot.py](scripts/fetch-alphaxiv-hot.py) as the default public fetcher.
- Use [scripts/materialize-curated-digest.py](scripts/materialize-curated-digest.py) to convert an agent-authored selection into final publish artifacts.
- Prefer [bin/bootstrap-paper-digest-lark-targets.sh](bin/bootstrap-paper-digest-lark-targets.sh) for first-run Feishu setup.

## Non-Negotiables

- Load durable config before deciding whether this is a publish run.
- Resolve the destination before preflight. Default to `feishu` for backward compatibility unless user preference says otherwise.
- For publish, scheduled, or automation runs, require the configured destination's publish fields and a notification target unless the user explicitly skips notification.
- If required destination config is missing, bootstrap first. Do not silently generate a local-only digest and call it done.
- Run a structured raw preview before curation and publishing.
- If a preference file exists, read it before selecting papers.
- The final `preview.json` and `digest.md` must represent the curated publish set, not the raw fetch output.
- Mark papers as seen only after destination publish and verification succeed.
- For Feishu, inspect publish JSON for `.ok == true`; do not rely on process exit code alone.
- Notify success, no-update, or failure for every publish/scheduled run.

## Workflow

1. **Preflight and config**
   - Source `${PAPER_DIGEST_CONFIG:-$HOME/.config/paper-digest/config.env}` if present.
   - Resolve `PAPER_DIGEST_DESTINATION` from explicit env, per-skill config, or global delivery preference. Default to `feishu` for backward compatibility.
   - Verify the fetcher and destination dependencies when publishing. See [references/setup.md](references/setup.md).

2. **Preview**
   - Run the fetcher with `--output json` and `--no-cache-write` to produce the raw candidate preview.
   - Optionally render a candidate markdown view for quick inspection.
   - Preserve raw candidate artifacts for validation and reporting.

3. **Curate and format**
   - Read `interested` and `excluded` preferences when configured.
   - Use the agent to semantically filter and rerank the candidate list.
   - Materialize the curated selection into the final `preview.json` and `digest.md`.
   - Validate heading levels before publishing. See [references/formatting.md](references/formatting.md).

4. **Publish**
   - Publish the Markdown digest to the configured destination.
   - Verify the destination write before claiming success.
   - Confirm the publish result is explicit success (`.ok == true` for Feishu, readback marker for Obsidian). See [references/workflow.md](references/workflow.md).

5. **Update dedupe state**
   - Append published paper IDs to `seen_ids.txt` only after destination publish and verification success.
   - Sort and deduplicate the cache file.

6. **Notify**
   - Send concise success, no-update, or failure status.
   - Include the destination reference.

## Final Report

Report:

- fetched, filtered, and published counts
- raw candidate count and curated count
- artifact paths
- destination publish/verification result
- notification result
- cache update result
- recovered errors and remaining follow-up
