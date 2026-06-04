#!/usr/bin/env bash
# hook: PreToolUse
# matcher: Bash(git commit:*)
# description: Warn (advisory, non-blocking) when cross-language duplication is detected (Lab 3)

set -euo pipefail

STAGED=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(py|go|java)$' || true)

if [[ -z "$STAGED" ]]; then
  exit 0
fi

echo "[shared-lib-check] Scanning for cross-language duplication..."

FINDINGS=$(claude --agent lib-extractor \
  -p "You are lib-extractor. Scan apps/user-service/app/services/, apps/notification-service/internal/service/, and apps/api-gateway/src/main/java/**/service/ for structurally duplicated functions or types (same logic or same field names/types in 2+ services). List each duplicate as: [DUPLICATE] name: found in N services. If none found, output: SHARED-LIB: CLEAN. If duplicates found, output: SHARED-LIB: DUPLICATES DETECTED (N)" \
  --output-format text 2>/dev/null || true)

if echo "$FINDINGS" | grep -q 'DUPLICATES DETECTED'; then
  echo "" >&2
  echo "[shared-lib-check] ADVISORY — Cross-language duplication found:" >&2
  echo "$FINDINGS" | grep '^\[DUPLICATE\]' >&2
  echo "" >&2
  echo "Consider running /extract-shared to scaffold libs/. This is advisory — commit is allowed." >&2
  # exit 0, not exit 2 — duplication is a smell, not a blocking error
fi

echo "[shared-lib-check] PASS — Commit allowed."
exit 0
