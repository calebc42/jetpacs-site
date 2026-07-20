#!/usr/bin/env bash
# Assemble the complete jetpacs.org docroot into public/.
# Self-contained and relative: works locally and on CI.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# CI resilience: build images ship their own (often old) Hugo — presence
# is not the contract, the pinned version is. Fetch ours unless the
# system hugo already matches.
V="${HUGO_VERSION:-0.164.0}"
if ! command -v hugo >/dev/null 2>&1 || ! hugo version 2>/dev/null | grep -q "v${V}"; then
  echo "pinned hugo v${V} not present — fetching hugo_extended ${V}"
  mkdir -p /tmp/hugo-bin
  curl -sSL "https://github.com/gohugoio/hugo/releases/download/v${V}/hugo_extended_${V}_linux-amd64.tar.gz" \
    | tar -xz -C /tmp/hugo-bin hugo
  export PATH="/tmp/hugo-bin:$PATH"
fi
hugo version
rm -rf public
mkdir -p public
# Root landing: index.org -> content/_index.md (ox-hugo, run _root/export.sh
# when the org changes) -> Hugo -> public/index.html.
echo "== hugo build: _root (landing)"
(cd _root && hugo --minify --gc --quiet)
cp -r _root/public/. public/
for s in jetpacs ebp glasspane jetpacs-composer; do
  echo "== hugo build: $s"
  (cd "$s" && hugo --minify --gc --quiet)
done
mkdir -p public/docs
cp -r jetpacs/public/. public/docs/
for s in ebp glasspane jetpacs-composer; do
  mkdir -p "public/$s/docs"
  cp -r "$s/public/." "public/$s/docs/"
done
KIT="$ROOT/_jetpacs-kit"
for s in ebp glasspane jetpacs-composer jelpa; do
  mkdir -p "public/$s"
  python3 "$KIT/gen-landing.py" "$KIT/content-$s.json" "public/$s/index.html"
  cp _root/static/jetpacs-icon.svg "public/$s/"
done
echo "docroot assembled at $ROOT/public"
