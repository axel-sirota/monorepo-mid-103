# Hook Registration Guide (Course 103)

When you build a craft agent (Labs 1–5), you'll need to register a hook in `.claude/settings.json` so it runs automatically when you commit code.

## Quick Start

1. **Create your hook script** (e.g., `.claude/hooks/style-check.sh`)
   ```bash
   #!/bin/bash
   # Run your craft agent or skill here
   echo "Checking style..."
   exit 0  # return 0 to allow commit, 1 to block
   ```

2. **Register it in `.claude/settings.json`**
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Bash",
           "hooks": [
             {
               "type": "command",
               "if": "Bash(git commit:*)",
               "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/style-check.sh"
             }
           ]
         }
       ]
     }
   }
   ```

## Hook Anatomy

Each hook in the `PreToolUse` array has three parts:

| Field | Meaning | Example |
|-------|---------|---------|
| `type` | Always `"command"` | `"command"` |
| `if` | When to run (git commit trigger) | `"Bash(git commit:*)"` |
| `command` | Path to your hook script | `"${CLAUDE_PROJECT_DIR}/.claude/hooks/style-check.sh"` |

**Key points:**
- Use `${CLAUDE_PROJECT_DIR}` as the repo root — it expands automatically
- The script runs **before** the `git commit` command executes
- Exit code `0` = allow commit to proceed; exit code `1` = block commit

## Testing Your Hook

Before committing code, dry-run your hook:

```bash
# Test it manually
bash .claude/hooks/style-check.sh

# Check the exit code
echo $?  # 0 = pass, 1 = fail
```

## Example: Style-Cop Hook (Lab 1)

```bash
#!/bin/bash
# .claude/hooks/style-check.sh

# Run the style-cop agent on the staged changes
# (Your Lab 1 implementation will do this)

echo "🎨 Running style-cop agent..."

# Placeholder: your style-cop agent call here
# If violations found, return 1 to block; otherwise return 0

exit 0
```

Then register it in `settings.json`:

```json
{
  "type": "command",
  "if": "Bash(git commit:*)",
  "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/style-check.sh"
}
```

## Existing Hooks (From Course 102)

The repo already has 5 persona-scoped hooks registered. You'll **ADD** to this list, not replace it:

- `engineer-check.sh` — runs before commit in `apps/`
- `designer-check.sh` — runs before commit in `frontend/`
- `pm-check.sh` — runs before commit in `prds/`
- `data-scientist-check.sh` — runs before commit in `ml/`
- `devops-check.sh` — runs before commit in `infra/`

Your craft-agent hooks (style-cop, contract-cop, lib-extractor, test-quality) will be **in addition** to these, operating cross-cluster.

## Debugging a Hook

If your hook blocks a commit unexpectedly:

1. **Check the hook script's exit code**
   ```bash
   bash .claude/hooks/style-check.sh
   echo $?
   ```

2. **Add debug output to the hook**
   ```bash
   #!/bin/bash
   set -x  # print commands as they run
   # ... your hook code
   ```

3. **Test without the hook temporarily**
   - Comment out the hook entry in `.claude/settings.json`
   - Run `make up` to verify the commit works
   - Uncomment and debug the hook script

## Reference: Hook JSON Structure

Full example with multiple hooks (don't copy this directly — use the pattern above):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git commit:*)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/engineer-check.sh"
          },
          {
            "type": "command",
            "if": "Bash(git commit:*)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/style-check.sh"
          }
        ]
      }
    ]
  }
}
```

Each hook in the array runs **in order** before the commit is allowed. If any returns exit code `1`, the commit is blocked.
