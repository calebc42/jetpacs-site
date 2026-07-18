#!/usr/bin/env bash
# Preview the whole jetpacs.org ecosystem locally.
#
# The built sites bake absolute https://jetpacs.org/... URLs into their
# cross-site nav (docs sidebars, sub-site landing headers). This copies the
# docroot to a throwaway dir, rewrites those absolute URLs to the local
# server so every link is clickable, then serves it.
#
# Usage: preview.sh [port]        (default 8000)
#   JETPACS_DOCROOT=... to point at a different build (default ~/publish-jetpacs)
set -euo pipefail

PORT="${1:-8000}"
SRC="${JETPACS_DOCROOT:-$(cd "$(dirname "$0")/.." && pwd)/public}"
PREVIEW="/tmp/jetpacs-preview"

[ -f "$SRC/index.html" ] || { echo "no built site at $SRC — run the build scripts first"; exit 1; }

rm -rf "$PREVIEW"
cp -r "$SRC" "$PREVIEW"
# Point the ecosystem's absolute links at this local server.
grep -rlZ 'https://jetpacs.org' "$PREVIEW" --include='*.html' 2>/dev/null \
  | xargs -0 -r sed -i "s|https://jetpacs.org|http://localhost:$PORT|g"

cat <<EOF
Serving the jetpacs.org ecosystem at http://localhost:$PORT/

  http://localhost:$PORT/                     foundation landing
  http://localhost:$PORT/docs/                foundation docs
  http://localhost:$PORT/ebp/                 protocol (+ /ebp/docs/)
  http://localhost:$PORT/jetpacs-composer/    composer (+ /docs/)
  http://localhost:$PORT/glasspane/           glasspane (+ /docs/)
  http://localhost:$PORT/jelpa/               JELPA (planned)

Cross-site links now resolve locally. Ctrl-C to stop.
EOF
exec python3 -m http.server "$PORT" --directory "$PREVIEW"
