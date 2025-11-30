#!/bin/bash
set -e                 # Exit immediately if any command fails

git add .
git commit -m "add2push" || true
git push

# --- Info ---
echo
echo "✅ Push complete! GitHub Pages is building in the background …"
echo "   Build status →  https://github.com/fantasy-mark/logseq_publish/actions "
echo "   Live preview →  https://fantasy-mark.github.io/logseq_publish/ "
echo