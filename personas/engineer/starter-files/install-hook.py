#!/usr/bin/env python3
"""Idempotently install the engineer persona's PreToolUse hook into .claude/settings.json.

Usage (from monorepo root):
    python3 personas/engineer/starter-files/install-hook.py

What it does:
  1. Ensures .claude/settings.json exists with a valid skeleton.
  2. Adds the engineer-required Bash permissions (make/docker/mvnw/uv/go/git).
  3. Registers .claude/hooks/engineer-check.sh as a PreToolUse hook on
     Bash(git commit *), creating the matcher block if missing.
  4. Re-runs are no-ops (won't duplicate entries).

This script touches ONLY the engineer persona's settings.  It is solo-safe:
running it on a clean repo produces a working engineer setup with no
knowledge of any other persona.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PERSONA = "engineer"
HOOK_COMMAND = "${CLAUDE_PROJECT_DIR}/.claude/hooks/engineer-check.sh"
HOOK_IF = "Bash(git commit:*)"
REQUIRED_PERMISSIONS = [
    "Bash(make:*)",
    "Bash(docker compose:*)",
    "Bash(docker:*)",
    "Bash(./mvnw:*)",
    "Bash(uv:*)",
    "Bash(go:*)",
    "Bash(git:*)",
]
SCHEMA = "https://json.schemastore.org/claude-code-settings.json"


def find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".claude").is_dir() or (p / "Makefile").is_file():
            return p
    return start


def load_settings(path: Path) -> dict:
    if not path.exists():
        return {"$schema": SCHEMA, "permissions": {"allow": []},
                "worktree": {"baseRef": "head"}, "hooks": {}}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: {path} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def ensure_permissions(settings: dict) -> None:
    perms = settings.setdefault("permissions", {})
    allow = perms.setdefault("allow", [])
    for entry in REQUIRED_PERMISSIONS:
        if entry not in allow:
            allow.append(entry)


def ensure_hook(settings: dict) -> None:
    hooks = settings.setdefault("hooks", {})
    pre = hooks.setdefault("PreToolUse", [])

    # Find or create the Bash matcher block.
    bash_block = None
    for block in pre:
        if block.get("matcher") == "Bash":
            bash_block = block
            break
    if bash_block is None:
        bash_block = {"matcher": "Bash", "hooks": []}
        pre.append(bash_block)

    inner = bash_block.setdefault("hooks", [])
    # Idempotency: skip if a hook with the same command is already present.
    for entry in inner:
        if entry.get("command") == HOOK_COMMAND and entry.get("if") == HOOK_IF:
            return
    inner.append({"type": "command", "if": HOOK_IF, "command": HOOK_COMMAND})


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = find_repo_root(script_dir)
    settings_path = repo_root / ".claude" / "settings.json"
    hook_target = repo_root / ".claude" / "hooks" / "engineer-check.sh"

    if not hook_target.exists():
        print(f"WARN: {hook_target} not present yet.  Run /set-persona {PERSONA} "
              f"first (it copies the hook script into .claude/hooks/).",
              file=sys.stderr)

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings = load_settings(settings_path)
    ensure_permissions(settings)
    ensure_hook(settings)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"OK: registered {PERSONA}-check hook in {settings_path}")

    if hook_target.exists():
        try:
            mode = hook_target.stat().st_mode
            hook_target.chmod(mode | 0o111)
            print(f"OK: ensured {hook_target} is executable")
        except OSError as e:
            print(f"WARN: could not chmod {hook_target}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
