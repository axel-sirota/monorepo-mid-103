#!/usr/bin/env bash
# hook: PreToolUse
# matcher: Bash(git commit:*)
# description: Block commits where consumer models drift from their JSON Schema contracts (Lab 2)

set -euo pipefail

STAGED=$(git diff --cached --name-only 2>/dev/null || true)

RELEVANT=$(echo "$STAGED" | grep -E \
  '(contracts/schemas/|apps/user-service/app/schemas/|apps/api-gateway/.*model/|apps/notification-service/internal/model/)' \
  || true)

if [[ -z "$RELEVANT" ]]; then
  exit 0
fi

echo "[contract-check] Contract-relevant files staged. Checking for drift..."
echo "$RELEVANT"

FINDINGS=$(claude --agent contract-cop \
  -p "Validate all contracts in contracts/schemas/ against their service implementations. Report only Critical findings." \
  --output-format text 2>/dev/null || true)

if echo "$FINDINGS" | grep -q '^\[Critical\]'; then
  echo "" >&2
  echo "[contract-check] BLOCKED — Schema drift detected:" >&2
  echo "$FINDINGS" | grep '^\[Critical\]' >&2
  echo "" >&2
  echo "Fix schema drift before committing. Schema and ALL consumers must be updated in the same commit." >&2
  exit 2
fi

echo "[contract-check] PASS — No contract drift."
exit 0
