---
description: Activate a persona pack (engineer, designer, pm, data-scientist, devops). Installs the persona's starter files into .claude/ and registers its pipeline + hooks.
---

# Set Persona Command

**When to use:** Run this first — before `/setup-stack`. Re-run at any time to switch personas; the previous install is cleaned first.

This command is the gateway to a persona pack. Each persona under `personas/{role}/` ships:

- `persona.md`, `README.md`, `SETUP.md`, `.env.example` — reference docs you read for context.
- `pipeline.yaml` — the persona's pipeline contract (copied to `.claude/pipeline.yaml`).
- `mcp.json`, `hooks.json` — optional MCP and editor hook configs.
- `starter-files/` — the actual installable bits (`agents/`, `skills/`, `hooks/`, `rules/`, `cluster/`, plus an `install-hook.py`).

`/set-persona` performs the install. Persona-specific *behavior* lives in the persona's skills and agents — there are no persona-specific slash commands in 102.

---

## Execution Flow

### Step 1: Detect Existing Persona

Read `.claude/.persona-manifest.json`.

- If the file exists: read `installed_paths` array. Show the user which persona is currently installed and list the files that will be removed. Ask for confirmation before continuing.
- If the file does not exist: proceed directly to Step 2 without prompting.

### Step 2: Show Persona Menu

List the subdirectories inside the `personas/` directory dynamically (do not hardcode names). For each subdirectory, read the first paragraph of `personas/{name}/README.md` to use as the description.

Present the menu like this:

```
Available personas:

1. {name}  — {first paragraph from personas/{name}/README.md}
2. ...

Which persona? (enter number or name)
```

Wait for the user to enter a number or a persona name. Validate the input; if it does not match any discovered subdirectory, print an error and re-prompt.

### Step 3: Validate Persona Pack

For the selected `{role}`, confirm the following exist (abort with a clear error if any are missing):

- `personas/{role}/pipeline.yaml`
- `personas/{role}/starter-files/install-hook.py`
- `personas/{role}/starter-files/` (directory)

Optional (only validated if present): `personas/{role}/mcp.json`, `personas/{role}/hooks.json`, `personas/{role}/.env.example`.

### Step 4: Remove Previous Persona

If a previous manifest was found in Step 1:

1. For each path listed in `installed_paths`, delete the file from disk. If a listed file no longer exists, warn `"Warning: {path} was already removed — skipping."` but continue.
2. Delete `.claude/.persona-manifest.json`.
3. Delete `.claude/pipeline.yaml` if it was listed in the manifest.
4. Print `"Previous persona ({name}) removed."`

If no previous manifest existed, skip this step silently.

### Step 5: Install Starter Files

Recursively copy the contents of `personas/{role}/starter-files/` into `.claude/`, **excluding** `install-hook.py` (that script stays in the persona pack — it is invoked from there in Step 7).

Concretely, for every file under `personas/{role}/starter-files/` other than `install-hook.py`:

- Source: `personas/{role}/starter-files/{relative-path}`
- Destination: `.claude/{relative-path}`

This means typical layouts are:

| Source under starter-files/ | Destination |
|---|---|
| `agents/*.md` | `.claude/agents/*.md` |
| `skills/{skill-name}/SKILL.md` (+ templates/) | `.claude/skills/{skill-name}/SKILL.md` |
| `hooks/*.sh` | `.claude/hooks/*.sh` (chmod +x) |
| `rules/*.md` | `.claude/rules/*.md` |
| `cluster/*.md` | `.claude/cluster/*.md` |

Before writing each destination, check whether it already exists AND was NOT listed in the previous manifest. If so, ask the user: `"Destination {path} already exists and was not installed by /set-persona. Overwrite or abort?"` and respect the answer.

Track every destination path written in this step in a list called `installed_paths`.

### Step 6: Install Persona Reference Config

Copy persona-level config files (only the ones that exist):

| Source | Destination | Notes |
|---|---|---|
| `personas/{role}/pipeline.yaml` | `.claude/pipeline.yaml` | Required. Activates pipeline-aware commands. |
| `personas/{role}/mcp.json` | `.claude/mcp.json` | Optional. Overwrite if present. |
| `personas/{role}/persona.md` | `.claude/persona.md` | Reference context for Claude. |

Add each written path to `installed_paths`.

Do **not** copy `personas/{role}/hooks.json` — hooks are managed by `install-hook.py` (which writes into `.claude/settings.json`).

### Step 7: Run install-hook.py

Run the persona's hook installer:

```bash
python3 personas/{role}/starter-files/install-hook.py
```

This script:
1. Ensures `.claude/settings.json` exists with the persona's required Bash permissions.
2. Registers PreToolUse / PostToolUse hooks that reference `.claude/hooks/*.sh` (which Step 5 copied).
3. Is idempotent — safe to re-run.

If the script exits non-zero, surface the error and abort. Do NOT roll back already-copied files (the manifest from Step 8 lets `/set-persona` clean up on the next run).

### Step 8: Update CLAUDE.md

Edit the project's `CLAUDE.md`:

- Find the `## Active Persona` section and set its value to `{role}`. If missing, add it.
- Find the `## Active Stack` section. If missing and the persona uses stacks (engineer, devops, data-scientist), add a placeholder noting `(set by /setup-stack)`. PM and designer personas omit this section.

If `CLAUDE.md` is just a placeholder (the "No Stack Configured" stub), replace it with:

```markdown
# Project Context

## Active Persona
{role}

## Active Stack
(set by /setup-stack — engineer, devops, and data-scientist personas only)
```

### Step 9: Write Manifest

Write the following JSON to `.claude/.persona-manifest.json`:

```json
{
  "persona": "{role}",
  "installed_at": "{ISO 8601 timestamp}",
  "pipeline": ".claude/pipeline.yaml",
  "installed_paths": [
    "... every path written in Steps 5 and 6 ..."
  ]
}
```

`installed_paths` must be a flat list of repo-relative paths. The manifest is what Step 4 reads to clean up on the next persona switch.

### Step 10: Print Confirmation Summary

Print a summary in this format (adapt to the actual install):

```
Persona active: {role}

Pipeline:        .claude/pipeline.yaml ({N} phases)
Skills loaded:   {list each .claude/skills/<name>/}
Agents loaded:   {list each .claude/agents/<name>.md}
Hooks active:    {list shell scripts registered by install-hook.py}
Rules:           {list .claude/rules/*.md}
MCP servers:     {list each server in .claude/mcp.json — or "(none)"}

Reference docs:
  personas/{role}/persona.md
  personas/{role}/README.md
  personas/{role}/SETUP.md
  personas/{role}/.env.example  (copy to .env if you have not already)

Next step:
  engineer       → Run /setup-stack to choose your tech stack
  data-scientist → Run /setup-stack to choose your tooling
  devops         → Run /setup-stack to choose your IaC stack
  pm             → Run /start-session
  designer       → Run /start-session
```

---

## Error Handling Reference

| Situation | Action |
|---|---|
| `personas/{role}/pipeline.yaml` missing | Abort. Report the missing path. Do not write any files. |
| `personas/{role}/starter-files/install-hook.py` missing | Abort with a clear message — the pack is incomplete. |
| Destination exists and NOT in previous manifest | Ask user: overwrite or abort. Respect their choice. |
| Manifest lists files that no longer exist on disk | Warn per file, continue cleaning the rest. |
| `install-hook.py` exits non-zero | Surface stderr, stop. The manifest from Step 8 (if written) lets the next run clean up. |
| User enters invalid persona name/number | Print error, re-show the menu. |

---

## Notes for Implementors

- The persona list is built by reading `personas/` at runtime. Never hardcode persona names.
- 102 is Claude Code only — no `.cursor/` paths are written.
- Persona-specific *commands* do not exist in 102. Persona behavior lives in `starter-files/skills/` and `starter-files/agents/`. The universal slash commands (`/code-review`, `/start-project`, `/start-session`, etc.) are persona-aware and branch internally based on `## Active Persona` in `CLAUDE.md`.
- The architect / start-session / next-session commands are pipeline-aware: they read `.claude/pipeline.yaml` (which Step 6 installs).
- This command is idempotent: re-running with the same persona produces a clean install (Step 4 removes the previous install before Step 5 copies fresh files).
- `/setup-stack` continues to work even if no persona has been set — but it will refuse stacks that do not match the persona once one is active.
