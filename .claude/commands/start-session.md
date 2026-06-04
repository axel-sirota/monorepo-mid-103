---
description: Verify persona contract is intact, then dispatch the persona's subagent for the active session
---

# /start-session — persona-agnostic session driver

Reads `.claude/pipeline.yaml`, verifies every artifact the persona promises
is actually present (subagent, skills, hooks, rules), then dispatches the
persona's subagent via the Task tool with the active session's goal as the
prompt. **No prose-only "the agent is now active"** — the Task call is the
mechanism.

---

## Step 0 — Read pipeline.yaml

```bash
test -f .claude/pipeline.yaml || { echo "no persona configured — run /set-persona first"; exit 1; }
```

Load the persona contract. Pull:
- `subagent.name`, `subagent.file`, `subagent.isolation`
- `skills[]` (`file` + `dispatches_subagents`)
- `hooks[]` (`matcher`, `if`, `command`)
- `rules[]`
- `cluster_claude_md`
- `architect_output.sessions_dir`

If pipeline.yaml is missing/malformed, FAIL with:
> "pipeline.yaml missing — copy from personas/<persona>/pipeline.yaml and re-run."

## Step 1 — Pick the active session

If `.claude/active-session` exists, read the session slug from it. Otherwise:

```bash
ls -1 <sessions_dir> | grep -E '^session-[0-9]+-.*\.md$' | grep -v 'done\.md$'
```

If zero pending sessions, FAIL with:
> "No pending sessions in <sessions_dir>. Run /architect to generate session plans."

If multiple, print the list and ask the user to pick one (number or slug).
Then write the chosen filename (without `.md`) to `.claude/active-session`.

Read the chosen `<sessions_dir>/session-N-<slug>.md`. Extract the `## Goal`
section verbatim — that becomes the subagent's prompt.

## Step 2 — Verify the persona's artifacts are PRESENT

For each artifact, run `test -f` (or for hooks, parse `.claude/settings.json`).
If ANY fails, refuse to dispatch and print every missing artifact with its
recovery hint. Do NOT proceed.

### 2a. Subagent file
```bash
test -f <subagent.file> || echo "MISSING: <subagent.file> — recover from personas/<persona>/starter-files/agents/<subagent.name>.md"
```

### 2b. Skills
For each `skills[].file`:
```bash
test -f <skill.file> || echo "MISSING: <skill.file> — recover from personas/<persona>/starter-files/skills/<skill.name>/"
```

For each `skills[].dispatches_subagents[]`, check the referenced agent file
exists. If not, WARN (don't fail) — the skill will fall back or break at
dispatch time:
> "WARN: skill <skill.name> dispatches subagent '<sub>' but .claude/agents/<sub>.md is not present. The skill will fail when it tries to dispatch."

### 2c. Hooks
Read `.claude/settings.json`. For each `hooks[]` entry, confirm a matching
PreToolUse → Bash matcher block contains a hook with the same `if` and
`command`. If missing:
> "MISSING hook: <command> not registered in .claude/settings.json — run `python3 personas/<persona>/starter-files/install-hook.py` from the repo root."

For the **devops** persona only: if pipeline.yaml has a `permissions_deny`
block, also confirm each entry is present in
`.claude/settings.json.permissions.deny[]`. If any is missing, print the
same install-hook.py recovery hint.

### 2d. Rules
For each `rules[]` path:
```bash
test -f <rule> || echo "MISSING: <rule> — recover from personas/<persona>/starter-files/rules/<basename>"
```

### 2e. Cluster CLAUDE.md
If `cluster_claude_md` is non-null:
```bash
test -f <cluster_claude_md> || echo "MISSING: <cluster_claude_md> — recover from personas/<persona>/starter-files/cluster/<basename>"
```

If ANY of 2a–2e failed, STOP. Print all failures together. Do not dispatch.

## Step 3 — Print readiness summary

```
✅ Persona contract verified for <persona>
   Subagent:  <subagent.name>  →  <subagent.file>
   Skills:    <skill.name>, ...
   Hooks:     <count> registered in .claude/settings.json (Bash(git commit:*))
   Rules:     <count> path-scoped rules present
   Cluster:   <cluster_claude_md or "—">

Active session: <session-N-slug>
   Goal: <verbatim from session file>
   Allowed scope: <scope.paths_allowed>
```

## Step 4 — Dispatch the persona's subagent via Task

This is the mechanism. PRINT what you're about to do, then call the Task tool:

```
Dispatching <subagent.name> via Task (isolation=<subagent.isolation>)...
```

Tool call:
```
Task(
  subagent_type: <subagent.name>,
  description: "Session <N>: <slug>",
  prompt: |
    Session goal: <goal from session file>

    Allowed scope (from pipeline.yaml):
      <scope.paths_allowed>
    Denied scope:
      <scope.paths_denied>

    Tasks (from <sessions_dir>/session-N-<slug>.md):
      <bullet list>

    Acceptance criteria:
      <bullet list>

    When you finish, run the persona's completion check:
      <completion_check.command>  (must exit <expect_exit>)
    Then summarize what changed and stop.
)
```

After Task returns, print a summary:

```
📋 Subagent <subagent.name> returned.
   Summary: <first 5 lines of agent output>

   Files changed: (git diff --stat)
   <output of: git diff --stat>

Next: when satisfied, run /next-session to close this session and prepare
the next one.
```

---

## Failure-loud rules

- pipeline.yaml missing → refuse with recovery hint.
- ANY artifact in 2a–2e missing → refuse with PER-FILE recovery hint.
- DO NOT silently proceed if a hook isn't registered. The student must see
  the missing hook and run install-hook.py.
- DO NOT claim "the subagent is active" without actually calling the Task
  tool. The agent_id appearing in the tool log IS the evidence.
- DO NOT prose-branch on persona name. Behavior comes from pipeline.yaml.
