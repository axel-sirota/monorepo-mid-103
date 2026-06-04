#!/usr/bin/env bash
# .claude/hooks/pm-check.sh
#
# PreToolUse hook on Bash(git commit:*).
# Blocks the commit if any staged file matching prds/NNNN-*.md (excluding
# _template.md and README.md) is missing required structural markers.
#
# Per-file checks:
#   1. At least one '## Story' or '### Story' heading.
#   2. At least one **Given** ... **When** ... **Then** triple.
#   3. A '## Non-functional requirements' or '## NFR' section is present.
#   4. No forbidden tokens left in the body: TODO, ??, TBD.
#      (HTML-commented <!-- TODO --> lines are exempt — drafts use them.)
#
# Exit 2 + stderr blocks the tool call and surfaces stderr to Claude as the
# error message. See https://code.claude.com/docs/en/hooks
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$PROJECT_DIR"

# Staged Markdown files under prds/, matching the NNNN-kebab.md pattern.
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null \
         | grep -E '^prds/[0-9]{4}-[a-z0-9-]+\.md$' \
         || true)

if [[ -z "$STAGED" ]]; then
  exit 0
fi

FAILURES=()

while IFS= read -r prd; do
  [[ -z "$prd" ]] && continue

  # Read the STAGED content (not the working-tree content) so the hook checks
  # what the commit would actually land.
  CONTENT=$(git show ":$prd" 2>/dev/null || true)
  if [[ -z "$CONTENT" ]]; then
    continue
  fi

  # Check 1: at least one Story heading (## or ### Story ...).
  STORY_COUNT=$(printf '%s\n' "$CONTENT" | grep -cE '^#{2,3} Story ' || true)
  if [[ "$STORY_COUNT" -lt 1 ]]; then
    FAILURES+=("$prd: no '## Story' or '### Story' heading found (need at least one INVEST story)")
  fi

  # Check 2: at least one Given/When/Then triple on a single line.
  GWT_COUNT=$(printf '%s\n' "$CONTENT" \
              | grep -cE '\*\*Given\*\*.*\*\*When\*\*.*\*\*Then\*\*' \
              || true)
  if [[ "$GWT_COUNT" -lt 1 ]]; then
    FAILURES+=("$prd: no '**Given** ... **When** ... **Then**' acceptance criterion found")
  fi

  # Check 3: NFR section present.
  if ! printf '%s\n' "$CONTENT" | grep -qE '^## (Non-functional requirements|NFR|[0-9]+\. Non-functional requirements)'; then
    FAILURES+=("$prd: missing '## Non-functional requirements' (or '## NFR') section")
  fi

  # Check 4: forbidden tokens in non-commented lines.
  #   - strip out HTML comment lines (single-line and the inside of inline comments at line scope)
  STRIPPED=$(printf '%s\n' "$CONTENT" | grep -vE '<!--.*-->' | grep -vE '^[[:space:]]*<!--' | grep -vE '^[[:space:]]*-->' || true)

  if printf '%s\n' "$STRIPPED" | grep -qE '\bTODO\b'; then
    BAD=$(printf '%s\n' "$STRIPPED" | grep -nE '\bTODO\b' | head -3)
    FAILURES+=("$prd: forbidden token TODO still present:"$'\n'"$BAD")
  fi
  if printf '%s\n' "$STRIPPED" | grep -qE '\bTBD\b'; then
    BAD=$(printf '%s\n' "$STRIPPED" | grep -nE '\bTBD\b' | head -3)
    FAILURES+=("$prd: forbidden token TBD still present:"$'\n'"$BAD")
  fi
  if printf '%s\n' "$STRIPPED" | grep -qE '\?\?'; then
    BAD=$(printf '%s\n' "$STRIPPED" | grep -nE '\?\?' | head -3)
    FAILURES+=("$prd: forbidden placeholder '??' still present:"$'\n'"$BAD")
  fi

done <<< "$STAGED"

if [[ "${#FAILURES[@]}" -gt 0 ]]; then
  echo "" >&2
  echo "PM-CHECK: commit blocked — PRD quality gate failed." >&2
  echo "------------------------------------------------------------" >&2
  for f in "${FAILURES[@]}"; do
    echo " - $f" >&2
  done
  echo "------------------------------------------------------------" >&2
  echo "Resolve and re-stage. See .claude/rules/pm.md for the full ruleset." >&2
  exit 2
fi

exit 0
