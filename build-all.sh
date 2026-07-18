#!/usr/bin/env bash
# Assemble the complete jetpacs.org docroot into public/.
# Self-contained and relative: works locally and on CI.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# CI resilience: some build images (e.g. Cloudflare's) ship no Hugo unless
# told to — provision our pinned version ourselves if it's missing.
if ! command -v hugo >/dev/null 2>&1; then
  V="${HUGO_VERSION:-0.164.0}"
  echo "hugo not found — fetching hugo_extended ${V}"
  mkdir -p /tmp/hugo-bin
  curl -sSL "https://github.com/gohugoio/hugo/releases/download/v${V}/hugo_extended_${V}_linux-amd64.tar.gz" \
    | tar -xz -C /tmp/hugo-bin hugo
  export PATH="/tmp/hugo-bin:$PATH"
fi
hugo version
rm -rf public
mkdir -p public
cp -r _root/. public/
for s in jetpacs ebp glasspane jetpacs-composer; do
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
  cp _root/jetpacs-icon.svg "public/$s/"
done
echo "docroot assembled at $ROOT/public"
