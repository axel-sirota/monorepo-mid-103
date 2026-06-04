#!/usr/bin/env bash
# engineer-check.sh — PreToolUse hook for Bash(git commit:*).
#
# Behavior:
#   - If `git diff --cached --name-only` shows any file under apps/, run `make test-apps`.
#   - On test failure, exit 2 with a clear stderr message (blocks the commit; Claude Code
#     surfaces stderr as the error message — see https://code.claude.com/docs/en/hooks).
#   - If no apps/ files staged, exit 0 quietly (no time wasted on unrelated commits).
#
# Portable bash only — no jq, no python.
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$PROJECT_DIR"

# Files staged for commit. PreToolUse fires BEFORE `git commit`, so the staged set is intact.
STAGED=$(git diff --cached --name-only 2>/dev/null || true)

# Did this commit touch apps/?
if ! echo "$STAGED" | grep -qE '^apps/'; then
  exit 0
fi

echo "engineer-check: apps/ files staged — running make test-apps" >&2

if ! make test-apps >&2; then
  echo "" >&2
  echo "BLOCKED: engineer-check hook — apps/ tests failed." >&2
  echo "Fix the failing tests, then retry the commit." >&2
  echo "" >&2
  echo "Re-run locally:  make test-apps" >&2
  exit 2
fi

echo "engineer-check: apps/ tests passed." >&2
exit 0
