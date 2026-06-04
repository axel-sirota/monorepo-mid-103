#!/usr/bin/env bash
# devops-check.sh — PreToolUse hook for Bash(git commit:*).
#
# Three blocks, all exit 2 + stderr to surface as Claude error message:
#   1. Refuse staged .tfstate / .tfstate.backup files.
#   2. For every staged *.tf under infra/, require a fresher *.tfplan in
#      infra/terraform_plans/ (newer mtime than the staged file).
#   3. Refuse staged shell/Make/yaml files that contain the literal string
#      "terraform destroy".
#
# Per Claude Code hooks docs: exit 2 + stderr blocks the tool call and
# surfaces stderr to Claude as the error message.
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$PROJECT_DIR"

# Helper: mtime of a file as a Unix timestamp, portable across macOS and Linux.
mtime() {
  local f="$1"
  case "$(uname -s)" in
    Darwin|*BSD) stat -f %m "$f" 2>/dev/null || echo 0 ;;
    *)           stat -c %Y "$f" 2>/dev/null || echo 0 ;;
  esac
}

STAGED=$(git diff --cached --name-only 2>/dev/null || true)

if [[ -z "$STAGED" ]]; then
  exit 0
fi

# ---------- Block 1: never commit terraform state ----------
TFSTATE_STAGED=$(echo "$STAGED" | grep -E '\.tfstate(\.backup)?$' || true)
if [[ -n "$TFSTATE_STAGED" ]]; then
  echo "" >&2
  echo "BLOCKED: devops-check — NEVER commit terraform state files." >&2
  echo "Staged tfstate files:" >&2
  echo "$TFSTATE_STAGED" | sed 's/^/  - /' >&2
  echo "" >&2
  echo "Add the following to .gitignore and unstage:" >&2
  echo "  *.tfstate" >&2
  echo "  *.tfstate.backup" >&2
  echo "Unstage with: git restore --staged <file>" >&2
  exit 2
fi

# ---------- Block 2: every staged infra/*.tf needs a fresh plan ----------
TF_STAGED=$(echo "$STAGED" \
  | grep -E '^infra/.*\.tf$' \
  | grep -vE '\.terraform\.lock\.hcl$' \
  || true)

if [[ -n "$TF_STAGED" ]]; then
  PLAN_DIR="infra/terraform_plans"
  if [[ ! -d "$PLAN_DIR" ]]; then
    echo "" >&2
    echo "BLOCKED: devops-check — staged .tf changes but no $PLAN_DIR/ directory." >&2
    echo "Run:" >&2
    echo "  cd infra/terraform && mkdir -p terraform_plans && \\" >&2
    echo "    terraform plan -out=terraform_plans/\$(date +%Y%m%d-%H%M%S).tfplan" >&2
    exit 2
  fi

  # Newest plan in the plans dir:
  NEWEST_PLAN=""
  NEWEST_PLAN_MTIME=0
  while IFS= read -r p; do
    [[ -z "$p" ]] && continue
    pm=$(mtime "$p")
    if (( pm > NEWEST_PLAN_MTIME )); then
      NEWEST_PLAN_MTIME=$pm
      NEWEST_PLAN=$p
    fi
  done < <(find "$PLAN_DIR" -maxdepth 1 -type f -name '*.tfplan' 2>/dev/null)

  if [[ -z "$NEWEST_PLAN" ]]; then
    echo "" >&2
    echo "BLOCKED: devops-check — staged .tf changes but no *.tfplan in $PLAN_DIR/." >&2
    echo "Run a plan before committing:" >&2
    echo "  cd infra/terraform && terraform plan -out=terraform_plans/\$(date +%Y%m%d-%H%M%S).tfplan" >&2
    exit 2
  fi

  STALE=""
  for f in $TF_STAGED; do
    [[ -f "$f" ]] || continue
    fm=$(mtime "$f")
    if (( fm > NEWEST_PLAN_MTIME )); then
      STALE="$STALE\n  - $f (modified after newest plan $NEWEST_PLAN)"
    fi
  done

  if [[ -n "$STALE" ]]; then
    echo "" >&2
    echo "BLOCKED: devops-check — staged .tf files are newer than the newest saved plan." >&2
    printf "%b\n" "$STALE" >&2
    echo "" >&2
    echo "Run a fresh plan before committing:" >&2
    echo "  cd infra/terraform && terraform plan -out=terraform_plans/\$(date +%Y%m%d-%H%M%S).tfplan" >&2
    exit 2
  fi

  echo "devops-check: staged .tf files have a fresh plan ($NEWEST_PLAN)." >&2
fi

# ---------- Block 3: refuse scripts that invoke terraform destroy ----------
SCRIPTY_STAGED=$(echo "$STAGED" \
  | grep -E '\.(sh|bash|zsh|mk|ya?ml)$|(^|/)Makefile$' \
  || true)

if [[ -n "$SCRIPTY_STAGED" ]]; then
  OFFENDERS=""
  for f in $SCRIPTY_STAGED; do
    [[ -f "$f" ]] || continue
    if grep -nE 'terraform[[:space:]]+destroy' "$f" >/dev/null 2>&1; then
      while IFS= read -r line; do
        OFFENDERS="$OFFENDERS\n  - $f: $line"
      done < <(grep -nE 'terraform[[:space:]]+destroy' "$f")
    fi
  done

  if [[ -n "$OFFENDERS" ]]; then
    echo "" >&2
    echo "BLOCKED: devops-check — staged file invokes 'terraform destroy'." >&2
    echo "Destroy is human-only per project policy; do not commit scripts that invoke it." >&2
    printf "%b\n" "$OFFENDERS" >&2
    exit 2
  fi
fi

exit 0
