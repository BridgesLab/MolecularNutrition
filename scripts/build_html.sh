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
    -s \
    --css=tufte.css \
    -o "html/${fname}.html"
done
