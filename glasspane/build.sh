#!/usr/bin/env bash
# Build the glasspane docs site and deploy into the jetpacs.org docroot.
# Usage: ./build.sh [destination]   (default: /home/calebc42/pkb/projects/jetpacs/jetpacs-site/public/glasspane/docs)
set -euo pipefail
SITE="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-/home/calebc42/pkb/projects/jetpacs/jetpacs-site/public/glasspane/docs}"
cd "$SITE"
hugo --minify --gc
rm -rf "$DEST"
mkdir -p "$DEST"
cp -r public/. "$DEST"/
echo "deployed to $DEST"
