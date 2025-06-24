#!/bin/bash

# Exit on errors
set -e

# Get directory of this script
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

cd "$REPO_ROOT"

for f in tex/*.tex; do
  fname=$(basename "$f" .tex)
  pandoc "$f" \
    --lua-filter=scripts/tufte.lua \
    --lua-filter=scripts/newthought.lua \
    --lua-filter=scripts/marginnotes.lua \
    -s \
    --css=tufte.css \
    --mathjax=https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js \
    --citeproc \
    --bibliography=tex/library.bib \
    -o "html/${fname}.html"
done
