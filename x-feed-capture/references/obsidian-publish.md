# X Feed Obsidian Publish

## Config

Required for `X_FEED_DESTINATION=obsidian`:

```bash
OBSIDIAN_VAULT_PATH="${OBSIDIAN_VAULT_PATH:?set destination vault path}"
```

Optional:

```bash
OBSIDIAN_VAULT_NAME="${OBSIDIAN_VAULT_NAME:-}"
X_FEED_OBSIDIAN_SUBDIR="${X_FEED_OBSIDIAN_SUBDIR:-Clippings/X Feed Capture}"
X_FEED_OBSIDIAN_FILE="${X_FEED_OBSIDIAN_FILE:-}"
```

Use an absolute `OBSIDIAN_VAULT_PATH`. Never hardcode a personal vault path in this public skill.
If `X_FEED_OBSIDIAN_FILE` is not set, publish to one monthly note named `YYYY-MM X Feed Capture.md`.

## Digest Shape

Prefer Markdown for Obsidian:

```markdown
## YYYY-MM-DD HH:MM

Fetched N posts and kept M high-value items.

### 1. Author - concise title

Summary under 100 Chinese characters or one short English sentence.

- Likes: N
- Reposts: N
- Original: https://x.com/user/status/id
```

Include a unique marker near the top:

```markdown
<!-- x-feed-capture:YYYY-MM-DDTHHMM -->
```

## Publish

Write one note per month. Each new batch is prepended near the top, immediately after YAML frontmatter when present, so the newest capture is first.

```bash
run_stamp="$(date '+%Y-%m-%dT%H%M')"
month_stamp="$(date '+%Y-%m')"
marker="<!-- x-feed-capture:${run_stamp} -->"
subdir="${X_FEED_OBSIDIAN_SUBDIR:-Clippings/X Feed Capture}"
title="X Feed Capture ${month_stamp}"
filename="${X_FEED_OBSIDIAN_FILE:-${month_stamp} X Feed Capture.md}"
dest_dir="${OBSIDIAN_VAULT_PATH}/${subdir}"
dest_path="${dest_dir}/${filename}"

mkdir -p "$dest_dir"
tmp_path="${dest_path}.tmp.$$"

if [[ ! -f "$dest_path" ]]; then
  {
    printf '%s\n' '---'
    printf 'title: "%s"\n' "$title"
    printf 'created: "%s"\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')"
    printf 'source: "x-feed-capture"\n'
    printf 'tags:\n  - x-feed-capture\n  - automation\n'
    printf '%s\n\n' '---'
  } > "$dest_path"
fi

awk -v marker="$marker" -v digest="$DIGEST_PATH" '
  function insert_batch() {
    if (inserted) return
    print marker
    print ""
    while ((getline line < digest) > 0) print line
    close(digest)
    print ""
    inserted = 1
  }
  NR == 1 && $0 == "---" {
    print
    in_fm = 1
    next
  }
  in_fm {
    print
    if ($0 == "---") insert_batch()
    next
  }
  NR == 1 {
    insert_batch()
  }
  { print }
  END {
    if (!inserted) insert_batch()
  }
' "$dest_path" > "$tmp_path"
mv "$tmp_path" "$dest_path"
```

`DIGEST_PATH` must point at the final Markdown payload, not raw extraction output.
The payload should not include document-level frontmatter because it is inserted into the monthly note body.
Before publishing, require it to exist and contain at least one canonical status URL:

```bash
test -s "$DIGEST_PATH"
batch_url="$(rg -o 'https://x\.com/[^[:space:])]+/status/[0-9]+' "$DIGEST_PATH" | head -n 1)"
test -n "$batch_url"
```

## Verify

Verify both the marker and at least one canonical status URL from the just-written batch. Do not verify with a generic `https://x.com/` search because older monthly entries can make that pass after a failed prepend:

```bash
rg -F "$marker" "$dest_path"
rg -F "$batch_url" "$dest_path"
```

The destination reference for notification/reporting is:

```bash
if [[ -n "${OBSIDIAN_VAULT_NAME:-}" ]]; then
  encoded_file="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "${subdir}/${filename}")"
  destination_ref="obsidian://open?vault=${OBSIDIAN_VAULT_NAME}&file=${encoded_file}"
else
  destination_ref="$dest_path"
fi
```

Advance `LAST_TIME` / `LAST_HREF` only after the readback checks pass and any enabled configured notification succeeds. If notifications are disabled by `X_FEED_NOTIFY=0`, skip notification and do not treat that as an exception.
