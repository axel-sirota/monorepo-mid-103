#!/usr/bin/env bash
# hook: PreToolUse
# matcher: Bash(git commit:*)
# description: Block commits with Critical style violations (Lab 1)

set -euo pipefail

STAGED=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(py|go|java|ts|tsx)$' || true)

if [[ -z "$STAGED" ]]; then
  exit 0
fi

echo "[style-check] Scanning staged files for Critical style violations..."
echo "$STAGED"

FINDINGS=$(claude --agent style-cop -p "Scan these files for style violations. List only Critical findings. Files: $(echo "$STAGED" | tr '\n' ' ')" --output-format text 2>/dev/null || true)

if echo "$FINDINGS" | grep -q '^\[Critical\]'; then
  echo "" >&2
  echo "[style-check] BLOCKED — Critical style violations found:" >&2
  echo "$FINDINGS" | grep '^\[Critical\]' >&2
  echo "" >&2
  echo "Fix the above violations and re-run git commit." >&2
  exit 2
fi

echo "[style-check] PASS — No Critical style violations."
exit 0
