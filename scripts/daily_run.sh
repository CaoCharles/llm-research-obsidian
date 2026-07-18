#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TZ="${TZ:-Asia/Taipei}"
DATE_STR="${1:-$(date +%F)}"
TOP_N="${TOP_N:-10}"
export OBSIDIAN_VAULT_PATH="${OBSIDIAN_VAULT_PATH:-$ROOT_DIR}"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Missing OPENAI_API_KEY; aborting." >&2
  exit 1
fi

cd "$ROOT_DIR"

# A clean checkout prevents a local run from accidentally committing unrelated work.
if [[ -n "$(git status --porcelain)" && "${ALLOW_DIRTY_WORKTREE:-0}" != "1" ]]; then
  echo "Working tree is not clean; commit/stash changes or set ALLOW_DIRTY_WORKTREE=1." >&2
  exit 1
fi

mkdir -p DailyJSON

uv sync --project lpdd --locked
uv run --project lpdd python lpdd/cli.py digest \
  --date "$DATE_STR" \
  --top "$TOP_N" \
  --out "DailyJSON/${DATE_STR}.json" \
  --write \
  --vault "$OBSIDIAN_VAULT_PATH" \
  --require-api-key

python3 scripts/sync_docs.py

# Keep the MkDocs environment outside OneDrive and outside the reusable skill
# assets, whose virtualenv shebangs become stale when a checkout is moved.
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/llm-paper-obsidian-mkdocs-venv}"
uv sync --project .agent/skills/mkdocs-setup/assets --locked --no-install-project
# The vault intentionally contains Obsidian wikilinks that MkDocs reports as
# warnings. Build the complete site, but do not turn those content warnings
# into a failed daily ingestion run.
uv run --project .agent/skills/mkdocs-setup/assets --no-sync mkdocs build --clean

git add -- Daily DailyJSON Papers Topics PDFs docs
if git diff --cached --quiet; then
  echo "No digest changes to commit."
  exit 0
fi

git commit -m "daily digest ${DATE_STR}"
git push
