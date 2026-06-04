#!/usr/bin/env bash
# data-scientist-check.sh — PreToolUse hook for Bash(git commit:*).
#
# Reproducibility gate for the data-scientist persona. Fires before any
# `git commit` and inspects staged ml/ files for:
#
#   1. ml/**/*.py that imports sklearn/numpy/torch but sets no seed
#      (random_state=, np.random.seed(, torch.manual_seed() -> BLOCK
#   2. ml/**/*.ipynb with code cells whose execution_count is null,
#      OR with out-of-order execution_count values -> BLOCK
#
# Exclusions for the seed check: tests/, conftest.py, __init__.py
# (fixtures legitimately use seeds only in setup, not in module body).
#
# Exit codes:
#   0  -> commit allowed
#   2  -> BLOCK (Claude Code surfaces stderr as the error message)
#
# Escape hatch:
#   BYPASS_DS_CHECK=1  -> allow commit, with a loud stderr warning.
#
# Requires: bash, grep, git, jq (for .ipynb parsing).
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$PROJECT_DIR"

# Only care about ml/.
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep -E '^ml/' || true)
if [[ -z "$STAGED" ]]; then
  exit 0
fi

VIOLATIONS=()

# ---- Check 1: Python files using sklearn/numpy/torch without a seed ----
PY_FILES=$(echo "$STAGED" \
  | grep -E '\.py$' \
  | grep -vE '(^|/)(tests?/|conftest\.py$|__init__\.py$)' \
  || true)

for f in $PY_FILES; do
  [[ -f "$f" ]] || continue

  # Heuristic: gate on "this file actually uses stochastic ML libs".
  if grep -qE '^[[:space:]]*(from|import)[[:space:]]+(sklearn|numpy|torch)([. ]|$)' "$f"; then
    if ! grep -qE '(random_state[[:space:]]*=|np\.random\.seed[[:space:]]*\(|numpy\.random\.seed[[:space:]]*\(|torch\.manual_seed[[:space:]]*\(|random\.seed[[:space:]]*\()' "$f"; then
      VIOLATIONS+=("SEED: $f imports sklearn/numpy/torch but sets no seed (need random_state= / np.random.seed( / torch.manual_seed()")
    fi
  fi
done

# ---- Check 2: Notebooks with unexecuted or out-of-order cells ----
IPYNB_FILES=$(echo "$STAGED" | grep -E '\.ipynb$' || true)

if [[ -n "$IPYNB_FILES" ]] && ! command -v jq >/dev/null 2>&1; then
  echo "data-scientist-check: jq is required for .ipynb checks (brew install jq / apt-get install jq)" >&2
  exit 2
fi

for f in $IPYNB_FILES; do
  [[ -f "$f" ]] || continue

  # Count code cells with execution_count = null AND non-empty source.
  UNEXEC=$(jq '[.cells[]
    | select(.cell_type=="code")
    | select((.source | join("") | gsub("\\s"; "")) != "")
    | select(.execution_count==null)] | length' "$f" 2>/dev/null || echo "JQERR")

  if [[ "$UNEXEC" == "JQERR" ]]; then
    VIOLATIONS+=("NB: $f is not valid JSON")
    continue
  fi

  if [[ "$UNEXEC" -gt 0 ]]; then
    VIOLATIONS+=("NB: $f has $UNEXEC code cell(s) with execution_count=null (unexecuted). Run the notebook top-to-bottom before commit.")
  fi

  # Out-of-order check: execution_counts of all executed code cells, in document order, must be strictly increasing.
  ORDER=$(jq -r '[.cells[] | select(.cell_type=="code") | select(.execution_count!=null) | .execution_count] | @csv' "$f" 2>/dev/null || echo "")
  if [[ -n "$ORDER" ]]; then
    PREV=0
    OK=1
    IFS=',' read -ra NUMS <<< "$ORDER"
    for n in "${NUMS[@]}"; do
      if (( n <= PREV )); then OK=0; break; fi
      PREV=$n
    done
    if [[ "$OK" -eq 0 ]]; then
      VIOLATIONS+=("NB: $f has out-of-order execution_count values ($ORDER). Restart kernel and run all cells before commit.")
    fi
  fi
done

if [[ ${#VIOLATIONS[@]} -gt 0 ]]; then
  echo "" >&2
  echo "data-scientist-check: COMMIT BLOCKED" >&2
  echo "" >&2
  for v in "${VIOLATIONS[@]}"; do
    echo "  - $v" >&2
  done
  echo "" >&2
  echo "Fix:" >&2
  echo "  - Add a seed: random_state=42, or numpy.random.seed(42)" >&2
  echo "  - For notebooks: run all cells top-to-bottom, save, then re-stage" >&2
  echo "" >&2
  echo "Escape hatch (not recommended): BYPASS_DS_CHECK=1 git commit ..." >&2

  if [[ "${BYPASS_DS_CHECK:-0}" == "1" ]]; then
    echo "" >&2
    echo "================================================================" >&2
    echo "  WARNING: BYPASS_DS_CHECK=1 set — reproducibility gate skipped." >&2
    echo "  This commit will land WITHOUT the data-scientist checks." >&2
    echo "  Note this in your experiment log if applicable." >&2
    echo "================================================================" >&2
    exit 0
  fi
  exit 2
fi

exit 0
