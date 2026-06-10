# X Feed Capture Gotchas

- Missing `~/.config/x-feed-capture/config.env` during a publish run is an onboarding gap. Run bootstrap before capture unless the user explicitly asked for dry run.
- `KIMI_WEBBRIDGE_URL` calls may return wrapped `evaluate` payloads under `data.value`; unwrap and null-check before parsing.
- `find_tab` may legitimately return no open X home tab. Open a fresh authenticated `https://x.com/home` tab and continue the real workflow.
- X's virtualized timeline can repeat visible cards while loading. Use large absolute scroll jumps with waits before declaring exhaustion.
- If page-side parser code fails with syntax errors, simplify DOM/string walking. Do not add more regex-heavy logic inside `evaluate`.
- Detail-page enrichment is valuable for truncated feed cards, but repeated empty bridge results should fall back to feed-card text rather than burning the run.
- Use `lark-cli docs +update --command block_insert_after --block-id ... --content ...`; older `--mode insert_after --markdown` and `--format` variants have failed in this environment.
- On this installed Lark CLI, use `docs +fetch --scope full` or `--scope keyword --keyword ...`; `--scope all` and `--query` are invalid.
- On this installed Lark CLI, `auth status --as user` is invalid; use `lark-cli auth status --verify`.
- If `${CODEX_HOME}` is unset for automation memory, default to `${HOME}/.codex`.
- If the stored anchor is stale, fetch live document IDs, repair `LARK_DOC_ANCHOR_BLOCK_ID` in durable config, republish, verify, then advance state.
