#!/usr/bin/env bash
# designer-check.sh — PreToolUse hook for Bash(git commit:*).
#
# Scans staged frontend/ files (.ts, .tsx, .css, .scss) for hardcoded design
# values (hex colors, px lengths). The frontend cluster's contract is:
# "tokens are the source of truth." A hardcoded literal is a bug.
#
# Per Claude Code hooks docs: exit 2 + stderr blocks the tool call AND
# surfaces stderr to Claude as the error message.
#
# Allowlist (intentionally NOT flagged):
#   - #fff, #000  (universal neutrals, used in occasional util classes)
#   - 0px, 1px    (border widths, layout primitives)
#   - lines inside /* ... */ block comments or // line comments
#   - hex/px values inside url(...) (e.g. SVG data URIs)

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$PROJECT_DIR"

# Files staged for commit, filtered to frontend/ .ts/.tsx/.css/.scss
STAGED=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
RELEVANT=$(printf "%s\n" "$STAGED" \
  | grep -E '^frontend/' \
  | grep -E '\.(tsx|ts|scss|css)$' \
  | grep -vE '/(dist|node_modules|storybook-static)/' \
  | grep -vE '\.test\.(tsx|ts)$' \
  | grep -vE '\.stories\.(tsx|ts)$' \
  || true)

if [[ -z "$RELEVANT" ]]; then
  exit 0
fi

VIOLATIONS=0
REPORT=""

# Strip common comment forms and url(...) payloads so we don't false-positive on them.
# Keeps line numbers via grep -n on the original; we re-check the matched line
# against a stripped version before reporting.
strip_noise() {
  # remove /* ... */ on the same line, // comments, and url(...) contents
  awk '{
    gsub(/\/\*[^*]*\*+([^\/*][^*]*\*+)*\//, "")
    sub(/\/\/.*/, "")
    gsub(/url\([^)]*\)/, "url()")
    print
  }'
}

scan_file() {
  local file="$1"

  # Pull staged blob (the version about to be committed), not the worktree copy.
  local content
  content=$(git show ":$file" 2>/dev/null || cat "$file" 2>/dev/null || true)
  [[ -z "$content" ]] && return 0

  # 1. Hex color literals: #RGB, #RGBA, #RRGGBB, #RRGGBBAA
  #    Allow: #fff and #000 (case-insensitive)
  while IFS= read -r hit; do
    [[ -z "$hit" ]] && continue
    local lineno="${hit%%:*}"
    local lineraw="${hit#*:}"
    local linestripped
    linestripped=$(printf "%s\n" "$lineraw" | strip_noise)
    # re-test on stripped version
    if printf "%s" "$linestripped" \
        | grep -iqE '#[0-9a-f]{3,8}\b' \
        && ! printf "%s" "$linestripped" \
        | grep -iqE '#(fff|000)\b' ; then
      REPORT="${REPORT}
  ${file}:${lineno}: hex color literal -> ${lineraw}"
      VIOLATIONS=$((VIOLATIONS + 1))
    fi
  done < <(printf "%s\n" "$content" | grep -niE '#[0-9a-f]{3,8}\b' || true)

  # 2. Pixel values: <digits>px
  #    Allow: 0px, 1px
  while IFS= read -r hit; do
    [[ -z "$hit" ]] && continue
    local lineno="${hit%%:*}"
    local lineraw="${hit#*:}"
    local linestripped
    linestripped=$(printf "%s\n" "$lineraw" | strip_noise)
    # Strip allowed px values (0px, 1px), then check what's left.
    # Use awk for portable word-boundary handling (BSD sed lacks \b).
    local pruned
    pruned=$(printf "%s" "$linestripped" | awk '{
      while (match($0, /(^|[^0-9A-Za-z])[01]px([^0-9A-Za-z]|$)/)) {
        # Keep the surrounding non-word chars; drop the [01]px in the middle.
        pre = substr($0, 1, RSTART - 1)
        seg = substr($0, RSTART, RLENGTH)
        # First and last chars of seg are the boundary chars (or empty if at edge)
        first = (RSTART == 1) ? "" : substr(seg, 1, 1)
        last  = (RSTART + RLENGTH - 1 == length($0)) ? "" : substr(seg, RLENGTH, 1)
        # Replace the [01]px (which is everything between first and last) with a space
        $0 = pre first " " last substr($0, RSTART + RLENGTH)
      }
      print
    }')
    if printf "%s" "$pruned" | grep -qE '(^|[^0-9A-Za-z])[0-9]+px([^0-9A-Za-z]|$)'; then
      REPORT="${REPORT}
  ${file}:${lineno}: px literal -> ${lineraw}"
      VIOLATIONS=$((VIOLATIONS + 1))
    fi
  done < <(printf "%s\n" "$content" | grep -nE '\b[0-9]+px\b' || true)
}

for f in $RELEVANT; do
  scan_file "$f"
done

if [[ "$VIOLATIONS" -gt 0 ]]; then
  {
    echo ""
    echo "BLOCKED: designer-check — ${VIOLATIONS} hardcoded design value(s) in staged frontend files."
    printf "%s\n" "$REPORT"
    echo ""
    echo "Use tokens from @monorepo/design-tokens instead:"
    echo "  - colors:  var(--color-*)        (see frontend/design-tokens/tokens/color.json)"
    echo "  - spacing: var(--spacing-*)      (see frontend/design-tokens/tokens/spacing.json)"
    echo "  - radii:   var(--radius-*)       (see frontend/design-tokens/tokens/radius.json)"
    echo "  - type:    var(--font-size-*)    (see frontend/design-tokens/tokens/typography.json)"
    echo ""
    echo "If no token fits, ADD one to the JSON and re-run 'npm run build:tokens' before committing."
  } >&2
  exit 2
fi

exit 0
