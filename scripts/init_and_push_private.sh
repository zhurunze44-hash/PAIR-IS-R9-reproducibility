#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v git >/dev/null || { echo "HOLD git not found"; exit 2; }
command -v gh >/dev/null || { echo "HOLD GitHub CLI not found"; exit 2; }
gh auth status >/dev/null || { echo "HOLD GitHub auth not configured"; exit 3; }
if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "HOLD: configure your own git user.name and user.email"; exit 4
fi
python3 scripts/publication_sanity.py
if [ -d .git ]; then
  echo "HOLD: already a git repository; inspect existing remote and commit manually"; exit 5
fi
git init -b main
git add .gitignore .gitattributes .github CITATION.cff README.md DATA_AND_CODE_AVAILABILITY.md NATIVE_DATA_REQUIREMENTS.md SUBMISSION_SOFTWARE_COVERAGE.md RELEASE_STATUS.json requirements-verified.txt evidence manuscript schemas scripts verification data/native/README.md
git diff --cached --stat
git commit -m 'Prepare R9 submission manuscript and exact-check software capsule'
gh repo create PAIR-IS-R9-reproducibility --private --source=. --remote=origin --push
printf "Private repository pushed; verify remote URL and release contents before changing visibility.\n"
