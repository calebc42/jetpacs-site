#!/usr/bin/env bash
# Sync curated Jetpacs docs from the repo's main branch into content/.
# The repo markdown is the source of truth — files written here are
# generated; edit them upstream in jetpacs/docs/ and re-run this script.
#
# Reads straight from git (not the working tree), so it doesn't matter
# which branch the checkout has out.
set -euo pipefail

REPO="${JETPACS_REPO:-/home/calebc42/pkb/projects/jetpacs/jetpacs}"
REF="${JETPACS_REF:-slop-fork/main}"
SITE="$(cd "$(dirname "$0")" && pwd)"
JETPACS_BLOB="https://github.com/calebc42/jetpacs/blob/slop-fork/main"
EBP_BLOB="https://github.com/calebc42/ebp/blob/main"

# filename (under docs/, no extension) : sidebar weight
DOCS="
TUTORIAL:10
ARCHITECTURE:20
BUILDING-TIER1:30
WIDGETS:40
BINDING:50
CONTRIBUTING-NODES:60
API-STABILITY:70
ROADMAP:80
"

for entry in $DOCS; do
  name="${entry%%:*}"
  weight="${entry##*:}"
  body="$(git -C "$REPO" show "${REF}:docs/${name}.md")"

  # Page title: the doc's first H1, falling back to the filename.
  title="$(printf '%s\n' "$body" | sed -n 's/^# //p' | head -1)"
  [ -n "$title" ] || title="$name"

  {
    printf -- '---\ntitle: "%s"\nweight: %s\n---\n\n' "${title//\"/\\\"}" "$weight"
    printf '%s\n' "$body" \
      | sed -E "s#\]\(\.\./ebp/#](${EBP_BLOB}/#g" \
      | sed -E "s#\]\(\.\./#](${JETPACS_BLOB}/#g" \
      | sed -E 's#\]\(\./#](#g' \
      | sed -E "s#\]\(([A-Za-z0-9._-]+\.el)\)#](${JETPACS_BLOB}/docs/\1)#g" \
      | sed -E "s#\]\(((PLAN|AUDIT|FOLLOWUP|DEMO)-[A-Za-z0-9._-]+\.md)(\#[A-Za-z0-9_-]+)?\)#](${JETPACS_BLOB}/docs/\1\3)#g"
  } > "$SITE/content/${name}.md"
  echo "synced ${name}.md (weight ${weight})"
done
