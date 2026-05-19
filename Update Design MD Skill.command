#!/bin/bash
set -euo pipefail

pause() {
  echo
  read -r -p "Press Return to close this window..." _ || true
}

finish() {
  code=$?
  if [[ $code -ne 0 ]]; then
    echo
    echo "Update failed. See the messages above."
  fi
  pause
  exit "$code"
}
trap finish EXIT

cd "$(dirname "$0")"

echo "Updating Design MD skill..."

if ! command -v git >/dev/null 2>&1; then
  echo "Git is not installed or not available in PATH."
  exit 1
fi

if [[ ! -d .git ]]; then
  echo "This updater must be inside the codex-design-md-skill git checkout."
  exit 1
fi

echo "Repository: $(pwd)"
echo "Fetching origin/main..."
git fetch --prune origin main

stashed=0
if [[ -n "$(git status --porcelain)" ]]; then
  stash_name="auto-stash before design-md skill update $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Saving local changes to git stash: $stash_name"
  git stash push -u -m "$stash_name"
  stashed=1
fi

if git show-ref --verify --quiet refs/heads/main; then
  git switch main
else
  git switch -c main --track origin/main
fi

if git merge-base --is-ancestor HEAD origin/main; then
  git merge --ff-only origin/main
else
  echo "Local main has commits that are not on origin/main."
  echo "Resolve that manually before using the one-click updater."
  exit 1
fi

echo
echo "Design MD skill is up to date."
echo "Current commit: $(git rev-parse --short HEAD)"

if [[ "$stashed" == "1" ]]; then
  echo
  echo "Local changes were saved in git stash."
  echo "Review them later with: git stash list"
fi

echo
echo "Open a new Codex thread, or restart Codex App if this skill was already loaded."
