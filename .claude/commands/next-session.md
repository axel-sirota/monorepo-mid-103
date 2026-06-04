---
description: Run the persona's transition checks, mark the active session done, prepare the next
---

# /next-session — persona-agnostic session transition

Reads `.claude/pipeline.yaml` and `.claude/active-session`, runs each command
in `session_transition_check`, refuses to transition if any check fails,
otherwise marks the session done and prints the next one's prompt.

---

## Step 0 — Read pipeline.yaml + active session

```bash
test -f .claude/pipeline.yaml || { echo "no persona configured — /next-session requires pipeline.yaml"; exit 1; }
test -f .claude/active-session || { echo "no active session — run /start-session first"; exit 1; }
```

Load:
- `session_transition_check[]` from pipeline.yaml
- `architect_output.sessions_dir`
- The active session slug from `.claude/active-session`

Compute the session file path: `<sessions_dir>/<active-session>.md`.

If that file doesn't exist, FAIL with:
> "Active session '<slug>' has no file at <path>. Either /start-session was never run, or someone deleted the file."

## Step 1 — Run every session_transition_check

For each entry, run the command. Capture exit code and stderr.

```
🔍 Running session_transition_check…

  [1/N] <name>:  <command>
        exit: <code>
        <command output if any>
```

If ANY check returns non-zero exit, REFUSE to transition:

```
⛔ Cannot transition — session_transition_check failed.

Failing check: <name>
Command:       <command>
Description:   <description>
Exit code:     <code>

Fix the underlying issue, then re-run /next-session.
```

STOP here. Do not mark the session done.

## Step 2 — All checks passed → mark session done

Rename the session file to mark completion:

```bash
mv <sessions_dir>/<slug>.md <sessions_dir>/<slug>-done.md
```

(If `<slug>-done.md` already exists, append a `.dupN` suffix instead of
overwriting. Loud over silent.)

## Step 3 — Write transition note

Append a transition record to the now-`-done.md` file:

```markdown

---

## Session Transition (closed by /next-session)

**Closed at:** <ISO timestamp>
**Verified via:** <list of session_transition_check names + commands>

**Changes summary:**
<output of: git log --oneline since session start, or "no commits this session">

**Files touched:**
<output of: git diff --stat HEAD~N..HEAD scoped to scope.paths_allowed>

**Next session:** <next pending session slug, or "—"> 
```

## Step 4 — Clear active marker, find next session

```bash
rm .claude/active-session
ls -1 <sessions_dir> | grep -E '^session-[0-9]+-.*\.md$' | grep -v 'done\.md$' | head -1
```

Capture the next pending session slug (if any).

## Step 5 — Print readiness for next session

If a next session exists:

```
✅ Session <slug> closed.

Next pending: <next-slug>
   Goal: <first line of ## Goal from next session file>

To begin: /start-session
```

If no pending sessions remain:

```
✅ Session <slug> closed.

🎉 No pending sessions in <sessions_dir>. All sessions from the architect
   plan are complete.

To plan more work: /architect "<next feature request>"
```

---

## Failure-loud rules

- Missing pipeline.yaml or active-session marker → refuse, name the missing
  file.
- Any failing session_transition_check → refuse, name the failing check by
  its `name` field, show exit code and command.
- Never auto-bypass a failing check. The student fixes the underlying issue
  and re-runs.
- Never claim "session closed" without actually renaming the file. The
  `-done.md` rename IS the evidence.
- Never lose the transition note — append before clearing the active marker.
