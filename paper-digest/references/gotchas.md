# Paper Digest Gotchas

- Missing destination config during a scheduled or publish run is a setup gap. Run Feishu or Obsidian bootstrap first unless the user explicitly asks for dry run.
- Do not update `seen_ids.txt` before destination publish and verification succeed. The dedupe cache is the commit point.
- Do not rely on `lark-cli` process exit code alone. Inspect `.ok == true` in publish JSON.
- Use a relative `@digest.md` path from the digest directory. Absolute `@/tmp/...` content paths can fail.
- For Feishu, keep `PAPER_DIGEST_DOC_URL` in config so notifications can include a stable document link.
- For Obsidian, a successful file write is not enough. Read back the note and verify the marker plus at least one H3 or arXiv link before updating `seen_ids.txt`.
- For Obsidian monthly notes, prepend the new digest block after frontmatter; do not append at the bottom or overwrite older monthly content.
- Default `${CODEX_HOME}` to `${HOME}/.codex` in strict shells before writing automation artifacts.
- Default `PAPER_DIGEST_CACHE_DIR` to `~/.cache/paper-digest` before using it under `set -u`.
- Keep `raw-preview.json` separate from the final curated `preview.json`; do not publish or advance dedupe state from the raw candidate preview.
- If `PAPER_DIGEST_PREFERENCES_FILE` exists, the final publish set should reflect it. Do not fall back to hidden hardcoded topic filters.
- Public skills must not include real Feishu/Lark document URLs, tokens, chat IDs, personal filesystem paths, cache files, or raw fetched data.
- If same-day artifacts already exist, rerun the workflow and treat the fresh run as authoritative rather than reporting stale files.
