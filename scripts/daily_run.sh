#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATE_STR="$(date +%F)"

export OBSIDIAN_VAULT_PATH="${OBSIDIAN_VAULT_PATH:-$ROOT_DIR}"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Missing OPENAI_API_KEY; aborting." >&2
  exit 1
fi

cd "$ROOT_DIR"

# Run digest (Top N controlled by lpdd/config.yaml)
cd lpdd
uv run python main.py --config config.yaml --keywords keywords.yaml --date "$DATE_STR"
cd "$ROOT_DIR"

# Sync MkDocs docs/
python3 scripts/sync_docs.py

# Optional MkDocs build if available
if command -v mkdocs >/dev/null 2>&1; then
  mkdocs build --clean
fi

# Git commit + push
if [[ -n "$(git status --porcelain)" ]]; then
  git add -A
  git commit -m "daily digest ${DATE_STR}"
  git push
else
  echo "No changes to commit."
fi
