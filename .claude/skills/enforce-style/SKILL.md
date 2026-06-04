---
name: enforce-style
description: Run style-cop across all files in the current diff and apply fixes. Use when asked to fix style, lint, or enforce coding standards across any service in the monorepo.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, Task
---

# Enforce style across the diff

## Step 1 — Get the diff

```bash
git diff --cached --name-only   # staged files (pre-commit)
# OR
git diff --name-only HEAD       # all changes since last commit
```

Filter to source files only (skip `.md`, `.json`, `.yaml`, `.lock`).

## Step 2 — Dispatch style-cop

```
Task(style-cop, "Scan these files for style violations:\n{newline-separated file list}")
```

Wait for the report.

## Step 3 — Parse findings

Split into Critical (must fix) and Warning (advisory). If zero Criticals, report Warnings and stop.

## Step 4 — Apply fixes

For each Critical with a clear mechanical fix, use `Read` then `Edit` to apply it. After all edits, re-dispatch style-cop to confirm zero Criticals remain. If a Critical cannot be auto-fixed, tell the user: "Cannot auto-fix: [finding]. Please resolve manually and re-run `/enforce-style`."
