#!/usr/bin/env bash
# Export index.org -> content/_index.md via ox-hugo (Emacs batch).
# index.org is the source of truth; content/_index.md is generated.
# Run this after editing index.org, then build with ../build-all.sh.
#
# Requires Emacs with ox-hugo installed (M-x package-install RET ox-hugo).
set -euo pipefail
SITE="$(cd "$(dirname "$0")" && pwd)"

emacs -Q --batch \
  --eval "(require 'package)" \
  --eval "(package-initialize)" \
  --eval "(unless (require 'ox-hugo nil t) (error \"ox-hugo not installed in this Emacs\"))" \
  --eval "(with-current-buffer (find-file-noselect \"$SITE/index.org\")
            (org-hugo-export-to-md))"

echo "exported $SITE/content/_index.md"
