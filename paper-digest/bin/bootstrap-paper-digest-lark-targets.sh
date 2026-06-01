#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Bootstrap durable Lark targets for paper-digest and save them into an env file.

Usage:
  bootstrap-paper-digest-lark-targets.sh [options]

Options:
  --doc-url URL            Existing docx/wiki URL to use as destination.
                           Saved as PAPER_DIGEST_DOC_URL for notifications.
  --doc-token TOKEN        Existing document token to use as destination.
  --create-doc             Create a new destination document.
  --doc-title TITLE        Title to use with --create-doc. Default: Paper Digest
  --anchor-id BLOCK_ID     Use this block ID directly as PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID.
  --anchor-text TEXT       Find the first block whose visible text contains TEXT.
                           Default: Paper Digest
  --chat-name NAME         Search this chat name and save the first oc_* chat_id.
  --notify-chat-id ID      Use this chat ID directly as PAPER_DIGEST_NOTIFY_CHAT_ID.
  --notify-as TYPE         Lark identity used for notifications: user|bot.
                           Default: user
  --identity TYPE          Lark identity for docs/chat bootstrap: user|bot.
                           Default: user
  --output PATH            Env file path. Default:
                           ~/.config/paper-digest/config.env
  --force                  Overwrite an existing output file.
  --skip-chat              Do not resolve or write PAPER_DIGEST_NOTIFY_CHAT_ID.
  --help                   Show this help.

Examples:
  bootstrap-paper-digest-lark-targets.sh \
    --doc-url "https://example.feishu.cn/docx/doxcn123" \
    --anchor-text "Paper Digest" \
    --chat-name "AI Digest"

  bootstrap-paper-digest-lark-targets.sh \
    --create-doc \
    --doc-title "Paper Digest" \
    --skip-chat
EOF
}

die() {
  echo "Error: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

extract_doc_token() {
  local input="$1"
  if [[ "$input" =~ /docx/([A-Za-z0-9]+)/? ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  if [[ "$input" =~ /wiki/([A-Za-z0-9]+)/? ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  if [[ "$input" =~ ^[A-Za-z0-9]+$ ]]; then
    printf '%s\n' "$input"
    return 0
  fi
  return 1
}

parse_doc_id() {
  jq -r '
    .data.document.document_id //
    .data.document_id //
    .document.document_id //
    .document_id //
    empty
  ' | head -n1
}

parse_doc_content() {
  jq -r '
    .data.document.content //
    .data.content //
    .document.content //
    .content //
    empty
  '
}

parse_chat_id() {
  jq -r '
    .data.chats[0].chat_id //
    .data.items[0].chat_id //
    .chats[0].chat_id //
    .items[0].chat_id //
    empty
  ' | head -n1
}

find_anchor_id() {
  local xml_file="$1"
  local anchor_text="$2"
  ANCHOR_TEXT="$anchor_text" perl -0ne '
    use strict;
    use warnings;
    my $needle = $ENV{ANCHOR_TEXT} // q{};
    while (/<([A-Za-z0-9:_-]+)\b[^>]*\bid="([^"]+)"[^>]*>(.*?)<\/\1>/sg) {
      my ($tag, $id, $inner) = ($1, $2, $3);
      my $text = $inner;
      $text =~ s/<[^>]+>/ /g;
      $text =~ s/\s+/ /g;
      $text =~ s/^\s+|\s+$//g;
      next if $text eq q{};
      if (index(lc($text), lc($needle)) >= 0) {
        print "$id\n";
        exit 0;
      }
    }
  ' "$xml_file"
}

print_anchor_candidates() {
  local xml_file="$1"
  perl -0ne '
    use strict;
    use warnings;
    my $count = 0;
    while (/<([A-Za-z0-9:_-]+)\b[^>]*\bid="([^"]+)"[^>]*>(.*?)<\/\1>/sg) {
      my ($tag, $id, $inner) = ($1, $2, $3);
      my $text = $inner;
      $text =~ s/<[^>]+>/ /g;
      $text =~ s/\s+/ /g;
      $text =~ s/^\s+|\s+$//g;
      next if $text eq q{};
      print "$id\t$tag\t$text\n";
      $count++;
      last if $count >= 20;
    }
  ' "$xml_file"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_FETCH_SCRIPT="${SKILL_DIR}/scripts/fetch-alphaxiv-hot.py"

DOC_URL=""
DOC_TOKEN=""
CREATE_DOC=0
DOC_TITLE="Paper Digest"
ANCHOR_ID=""
ANCHOR_TEXT="Paper Digest"
CHAT_NAME=""
NOTIFY_CHAT_ID=""
NOTIFY_AS="user"
IDENTITY="user"
OUTPUT_PATH="${HOME}/.config/paper-digest/config.env"
FORCE=0
SKIP_CHAT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --doc-url)
      DOC_URL="${2:-}"
      shift 2
      ;;
    --doc-token)
      DOC_TOKEN="${2:-}"
      shift 2
      ;;
    --create-doc)
      CREATE_DOC=1
      shift
      ;;
    --doc-title)
      DOC_TITLE="${2:-}"
      shift 2
      ;;
    --anchor-id)
      ANCHOR_ID="${2:-}"
      shift 2
      ;;
    --anchor-text)
      ANCHOR_TEXT="${2:-}"
      shift 2
      ;;
    --chat-name)
      CHAT_NAME="${2:-}"
      shift 2
      ;;
    --notify-chat-id)
      NOTIFY_CHAT_ID="${2:-}"
      shift 2
      ;;
    --notify-as)
      NOTIFY_AS="${2:-}"
      shift 2
      ;;
    --identity)
      IDENTITY="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT_PATH="${2:-}"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --skip-chat)
      SKIP_CHAT=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

need_cmd lark-cli
need_cmd jq
need_cmd perl

[[ "$IDENTITY" == "user" || "$IDENTITY" == "bot" ]] || die "--identity must be user or bot"
[[ "$NOTIFY_AS" == "user" || "$NOTIFY_AS" == "bot" ]] || die "--notify-as must be user or bot"
[[ -x "$DEFAULT_FETCH_SCRIPT" || -f "$DEFAULT_FETCH_SCRIPT" ]] || die "missing bundled fetch script: $DEFAULT_FETCH_SCRIPT"

if [[ -n "$DOC_URL" && -n "$DOC_TOKEN" ]]; then
  die "pass only one of --doc-url or --doc-token"
fi

if [[ "$CREATE_DOC" -eq 1 && ( -n "$DOC_URL" || -n "$DOC_TOKEN" ) ]]; then
  die "--create-doc cannot be combined with --doc-url or --doc-token"
fi

if [[ "$SKIP_CHAT" -eq 0 && -z "$NOTIFY_CHAT_ID" && -z "$CHAT_NAME" ]]; then
  echo "Notice: no chat target configured; the env file will omit PAPER_DIGEST_NOTIFY_CHAT_ID." >&2
fi

if [[ -e "$OUTPUT_PATH" && "$FORCE" -ne 1 ]]; then
  die "output already exists: $OUTPUT_PATH (use --force to overwrite)"
fi

if [[ -n "$DOC_URL" ]]; then
  DOC_TOKEN="$(extract_doc_token "$DOC_URL")" || die "failed to extract doc token from URL"
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

if [[ "$CREATE_DOC" -eq 1 ]]; then
  create_xml="<title>${DOC_TITLE}</title><h1>${DOC_TITLE}</h1><p>Newest digest entries are inserted below this heading.</p>"
  echo "Creating Lark document: ${DOC_TITLE}" >&2
  lark-cli docs +create --api-version v2 --as "$IDENTITY" --content "$create_xml" >"$tmpdir/create.json"
  DOC_TOKEN="$(parse_doc_id <"$tmpdir/create.json")"
  [[ -n "$DOC_TOKEN" ]] || die "could not parse document_id from docs +create output"
fi

[[ -n "$DOC_TOKEN" ]] || die "missing document target; pass --doc-url, --doc-token, or --create-doc"

echo "Fetching document with block IDs for configured document" >&2
lark-cli docs +fetch --api-version v2 --as "$IDENTITY" --doc "$DOC_TOKEN" --detail with-ids >"$tmpdir/fetch.json"
parse_doc_content <"$tmpdir/fetch.json" >"$tmpdir/document.xml"

if [[ ! -s "$tmpdir/document.xml" ]]; then
  die "could not parse document content from docs +fetch output"
fi

if [[ -z "$ANCHOR_ID" ]]; then
  ANCHOR_ID="$(find_anchor_id "$tmpdir/document.xml" "$ANCHOR_TEXT" || true)"
fi

if [[ -z "$ANCHOR_ID" ]]; then
  echo "Could not auto-resolve an anchor block containing: ${ANCHOR_TEXT}" >&2
  echo "Top anchor candidates from the document:" >&2
  print_anchor_candidates "$tmpdir/document.xml" | sed 's/^/  /' >&2 || true
  die "re-run with --anchor-id <blk...> or choose a better --anchor-text"
fi

if [[ -z "$NOTIFY_CHAT_ID" && "$SKIP_CHAT" -eq 0 && -n "$CHAT_NAME" ]]; then
  echo "Searching notify chat: ${CHAT_NAME}" >&2
  lark-cli im +chat-search --as "$IDENTITY" --query "$CHAT_NAME" >"$tmpdir/chat-search.json"
  NOTIFY_CHAT_ID="$(parse_chat_id <"$tmpdir/chat-search.json")"
  [[ -n "$NOTIFY_CHAT_ID" ]] || die "could not resolve chat_id from im +chat-search output"
fi

mkdir -p "$(dirname "$OUTPUT_PATH")"

{
  printf 'PAPER_DIGEST_FETCH_SCRIPT=%q\n' "$DEFAULT_FETCH_SCRIPT"
  printf 'PAPER_DIGEST_DOC_TOKEN=%q\n' "$DOC_TOKEN"
  if [[ -n "$DOC_URL" ]]; then
    printf 'PAPER_DIGEST_DOC_URL=%q\n' "$DOC_URL"
  fi
  printf 'PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID=%q\n' "$ANCHOR_ID"
  printf 'PAPER_DIGEST_DOC_AS=%q\n' "$IDENTITY"
  printf 'PAPER_DIGEST_NOTIFY_AS=%q\n' "$NOTIFY_AS"
  if [[ -n "$NOTIFY_CHAT_ID" ]]; then
    printf 'PAPER_DIGEST_NOTIFY_CHAT_ID=%q\n' "$NOTIFY_CHAT_ID"
  fi
} >"$OUTPUT_PATH"

chmod 600 "$OUTPUT_PATH"

cat <<EOF
Bootstrap complete.

Saved:
  $OUTPUT_PATH

Resolved values:
  PAPER_DIGEST_FETCH_SCRIPT=$DEFAULT_FETCH_SCRIPT
  PAPER_DIGEST_DOC_TOKEN=<saved>
EOF

if [[ -n "$DOC_URL" ]]; then
  echo "  PAPER_DIGEST_DOC_URL=<saved>"
else
  echo "  PAPER_DIGEST_DOC_URL=<unset>"
fi

cat <<EOF
  PAPER_DIGEST_DOC_ANCHOR_BLOCK_ID=<saved>
  PAPER_DIGEST_DOC_AS=$IDENTITY
  PAPER_DIGEST_NOTIFY_AS=$NOTIFY_AS
EOF

if [[ -n "$NOTIFY_CHAT_ID" ]]; then
  printf '  PAPER_DIGEST_NOTIFY_CHAT_ID=%s\n' "$NOTIFY_CHAT_ID"
else
  echo "  PAPER_DIGEST_NOTIFY_CHAT_ID=<unset>"
fi

echo
echo "Next step:"
echo "  source \"$OUTPUT_PATH\""
