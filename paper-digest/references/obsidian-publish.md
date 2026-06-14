# Paper Digest Obsidian Publish

## Config

Required for `PAPER_DIGEST_DESTINATION=obsidian`:

```bash
OBSIDIAN_VAULT_PATH="${OBSIDIAN_VAULT_PATH:?set destination vault path}"
```

Optional:

```bash
OBSIDIAN_VAULT_NAME="${OBSIDIAN_VAULT_NAME:-}"
PAPER_DIGEST_OBSIDIAN_SUBDIR="${PAPER_DIGEST_OBSIDIAN_SUBDIR:-Papers/Digests}"
PAPER_DIGEST_OBSIDIAN_FILE="${PAPER_DIGEST_OBSIDIAN_FILE:-}"
```

Use an absolute `OBSIDIAN_VAULT_PATH`. Never hardcode a personal vault path in this public skill.
If `PAPER_DIGEST_OBSIDIAN_FILE` is not set, publish to one monthly note named `YYYY-MM Paper Digest.md`.

## Note Shape

Write one note per month and prepend the latest run near the top:

```markdown
---
title: "YYYY-MM Paper Digest"
created: "YYYY-MM-DDTHH:MM:SS+0800"
source: "paper-digest"
tags:
  - paper-digest
  - automation
---

<!-- paper-digest:YYYY-MM-DDTHHMMSS -->

## YYYY-MM-DD Paper Digest

### Paper Title
...
```

Keep the existing digest heading rules from [formatting.md](formatting.md): exactly one H2 run title and one H3 per paper.

## Publish

Use one monthly file and prepend each new digest block immediately after YAML frontmatter so the newest run is first. The per-run digest body should not contain document-level frontmatter.

```bash
run_date="$(date '+%Y-%m-%d')"
run_stamp="$(date '+%Y-%m-%dT%H%M%S')"
subdir="${PAPER_DIGEST_OBSIDIAN_SUBDIR:-Papers/Digests}"
filename="${PAPER_DIGEST_OBSIDIAN_FILE:-$(date '+%Y-%m') Paper Digest.md}"

python3 paper-digest/scripts/publish-obsidian-monthly.py \
  --vault-path "$OBSIDIAN_VAULT_PATH" \
  --vault-name "${OBSIDIAN_VAULT_NAME:-}" \
  --subdir "$subdir" \
  --digest-path "$DIGEST_PATH" \
  --preview-path preview.json \
  --run-date "$run_date" \
  --run-stamp "$run_stamp" \
  --output-json publish.json

jq -e '.ok == true' publish.json >/dev/null
```

`DIGEST_PATH` must point at the final validated Markdown digest.

## Verify

Verify the marker and at least one published paper link or H3:

```bash
marker="$(jq -r '.marker' publish.json)"
dest_path="$(jq -r '.dest_path' publish.json)"
rg -F "$marker" "$dest_path"
rg -n '^### ' "$dest_path"
```

If `preview.json` contains paper IDs, verify at least one concrete arXiv URL from the just-published digest:

```bash
first_url="$(jq -r '.papers[0].arxiv_url // empty' preview.json)"
if [[ -n "$first_url" ]]; then
  rg -F "$first_url" "$dest_path"
fi
```

The destination reference for notification/reporting is:

```bash
destination_ref="$(jq -r '.destination_ref' publish.json)"
```

Append paper IDs to `seen_ids.txt` only after the readback checks pass and notification succeeds or is explicitly skipped.
