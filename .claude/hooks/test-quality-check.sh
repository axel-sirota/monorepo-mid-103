#!/usr/bin/env bash
# hook: PreToolUse
# matcher: Bash(git commit:*)
# description: Block commits with hollow tests (zero assertions) in staged test files (Lab 4)

set -euo pipefail

STAGED_TESTS=$(git diff --cached --name-only 2>/dev/null | grep -E 'tests?/.*\.(py|go|java)$' || true)

if [[ -z "$STAGED_TESTS" ]]; then
  exit 0
fi

echo "[test-quality-check] Staged test files found. Checking for hollow tests..."
echo "$STAGED_TESTS"

HOLLOW=0

# Fast grep check: find test functions with no assertion in the next 10 lines
while IFS= read -r file; do
  if [[ "$file" == *.py ]]; then
    # Python: find def test_ with no assert in the function body
    python3 - "$file" <<'PYEOF'
import sys, re

content = open(sys.argv[1]).read()
functions = re.split(r'\n(?=    def test_|\ndef test_)', content)
for fn in functions:
    if not re.match(r'\s*def test_', fn):
        continue
    name_match = re.search(r'def (test_\w+)', fn)
    name = name_match.group(1) if name_match else "unknown"
    if 'assert' not in fn and 'assertEqual' not in fn and 'assertTrue' not in fn:
        print(f"[HOLLOW] {sys.argv[1]}: {name} — zero assertions")
        sys.exit(1)
PYEOF
    HOLLOW=$((HOLLOW + $?))
  fi
done <<< "$STAGED_TESTS"

if [[ $HOLLOW -gt 0 ]]; then
  echo "" >&2
  echo "[test-quality-check] BLOCKED — Hollow tests detected (zero assertions)." >&2
  echo "A test with no assert proves the function doesn't crash — nothing about what it returns." >&2
  echo "Add at least one assert statement to each test function." >&2
  exit 2
fi

echo "[test-quality-check] PASS — No hollow tests detected."
exit 0
