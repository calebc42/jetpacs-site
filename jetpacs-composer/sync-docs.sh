#!/usr/bin/env bash
# Re-sync jetpacs-composer docs from the repo and rewrite links. Edit upstream, not here.
set -euo pipefail
SITE="$(cd "$(dirname "$0")" && pwd)"
python3 "$SITE/../_jetpacs-kit/sync-docs.py" "$SITE/sync.config.json"
