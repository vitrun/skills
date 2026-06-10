# Paper Digest Gotchas

- Missing publish config during a scheduled or publish run is a setup gap. Run bootstrap first unless the user explicitly asks for dry run.
- Do not update `seen_ids.txt` before document publish succeeds. The dedupe cache is the commit point.
- Do not rely on `lark-cli` process exit code alone. Inspect `.ok == true` in publish JSON.
- Use a relative `@digest.md` path from the digest directory. Absolute `@/tmp/...` content paths can fail.
- Keep `PAPER_DIGEST_DOC_URL` in config so notifications can include a stable document link.
- Default `${CODEX_HOME}` to `${HOME}/.codex` in strict shells before writing automation artifacts.
- Default `PAPER_DIGEST_CACHE_DIR` to `~/.cache/paper-digest` before using it under `set -u`.
- Public skills must not include real Feishu/Lark document URLs, tokens, chat IDs, personal filesystem paths, cache files, or raw fetched data.
- If same-day artifacts already exist, rerun the workflow and treat the fresh run as authoritative rather than reporting stale files.
