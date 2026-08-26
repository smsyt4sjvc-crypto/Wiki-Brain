#!/usr/bin/env bash
# Mirror the current research-vault/ state onto Wiki-Brain main as ONE commit.
#
# ⛔ NEVER `git pull --rebase wb main` from the INMA- checkout. Wiki-Brain main
# is a ROOT-LEVEL mirror of research-vault/ (different SHAs, no shared history)
# plus files of its own (work/, cron-written data/fragility/*). A rebase
# replays ancient INMA site commits onto it and publishes junk — proven
# 2026-08-25, when a conflicted rebase push landed a stray root Index.html on
# Wiki-Brain main (reverted by commit 8b9c821).
#
# This script instead grafts the vault state onto wb/main's tree via a temp
# index: wb-only content (work/, newer cron data) is preserved untouched;
# every path the VAULT OWNS is synced to HEAD, including deletions.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

git fetch wb main -q
WB=$(git rev-parse FETCH_HEAD)
MSG="${1:-$(git log -1 --pretty=%s)}"

# Dirs/files whose contents the vault is authoritative for on Wiki-Brain.
# NOT data/ (the weekday fragility cron writes data/fragility/* on wb main —
# its copy can be NEWER than ours) and NOT work/ (wb-only).
OWNED='wiki chat-log tools predictions raw docs handoffs backtest CLAUDE.md index.md'

IDX=$(mktemp)
trap 'rm -f "$IDX"' EXIT
export GIT_INDEX_FILE="$IDX"
git read-tree "$WB"

# Drop wb's copy of every owned path, then overlay HEAD's research-vault copy.
for p in $OWNED; do
  git ls-tree -r --name-only "$WB" -- "$p" 2>/dev/null | while read -r f; do
    git update-index --force-remove "$f"
  done
  git ls-tree -r "HEAD:research-vault" -- "$p" 2>/dev/null \
  | while read -r mode type blob path; do
    git update-index --add --cacheinfo "$mode,$blob,$path"
  done
done

TREE=$(git write-tree)
unset GIT_INDEX_FILE
if [ "$TREE" = "$(git rev-parse "$WB^{tree}")" ]; then
  echo "wb/main already matches — nothing to push"
  exit 0
fi
NEW=$(git commit-tree "$TREE" -p "$WB" -m "$MSG")
git push wb "$NEW:main"
echo "pushed $NEW -> wb/main"
