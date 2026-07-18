#!/usr/bin/env bash
# Stamp a new jetpacs.org sub-site from the shared kit.
# Usage: scaffold.sh <slug>
# Copies the vendored theme + shared assets (palette, chroma, copy button,
# inject partial, icon) into ~/pkb/sites/<slug>/. Per-site files (hugo.toml,
# content/, sync-docs.sh, build.sh) are written separately.
#
# Re-running is safe: it refreshes the shared assets from the kit (that's how
# the four sites stay visually identical — edit the kit, re-scaffold, rebuild).
set -euo pipefail

SLUG="${1:?usage: scaffold.sh <slug>}"
KIT="$(cd "$(dirname "$0")" && pwd)"
SITE="$HOME/pkb/sites/$SLUG"

mkdir -p "$SITE/assets" "$SITE/content" "$SITE/static" "$SITE/layouts/_partials/docs/inject"

# Theme (wholesale, kept in sync with the kit).
rm -rf "$SITE/themes/hugo-book"
mkdir -p "$SITE/themes/hugo-book"
cp -r "$KIT/themes/hugo-book/." "$SITE/themes/hugo-book/"

# Shared, must-stay-in-sync assets.
cp "$KIT/assets/"* "$SITE/assets/"
cp "$KIT/layouts/_partials/docs/inject/body.html" "$SITE/layouts/_partials/docs/inject/body.html"
cp "$KIT/static/jetpacs-icon.svg" "$SITE/static/"

echo "scaffolded $SITE from kit"
