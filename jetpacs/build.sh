#!/usr/bin/env bash
# Build the docs site and deploy it into the jetpacs.org publish docroot.
# Usage: ./build.sh [destination]   (default: ~/publish-jetpacs/docs)
set -euo pipefail

SITE="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-$SITE/../public/docs}"

cd "$SITE"
hugo --minify --gc
# The destination is fully generated output — replace it wholesale.
rm -rf "$DEST"
mkdir -p "$DEST"
cp -r public/. "$DEST"/
echo "deployed to $DEST"
