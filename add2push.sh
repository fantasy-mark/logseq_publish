#!/bin/bash
# Stash local changes first
git stash push -m "WIP: $(date +%H:%M)"

# Pull updates with rebase (stops at current branch when conflicts occur, no merge commit generated)
git pull --rebase origin $(git branch --show-current)

# Restore stash after resolving conflicts (if any)
git stash pop

# Safe add: only add tracked modifications, or specify files explicitly
git add -u  # Only add modifications to tracked files
# Or: git add src/ tests/  # Specify directories explicitly

# Check if there is anything to commit
if git diff --cached --quiet; then
    echo "ℹ️ No changes to commit"
else
    git commit -m "feat: your descriptive message here"
    git push
fi

# Check if there are untracked modifications in the working directory
if ! git diff-index --quiet HEAD --; then
    git add -u
    git commit -m "update: $(date '+%Y-%m-%d %H:%M')" 
    git push
    echo
    echo " Push complete! GitHub Pages is building in the background ..."
    echo
    echo "   Build status ->  https://github.com/fantasy-mark/logseq_publish/actions "
    echo "   Live preview ->  https://fantasy-mark.github.io/logseq_publish/ "
    echo
else
    echo "ℹ️  Working directory is clean, no commits needed"
fi