---
name: review-pr-parallel
description: Parallel PR review — dispatches all 5 craft agents simultaneously via Agent Teams, then synthesizes verdict. Faster than /review-pr on large diffs (~90s vs ~4.5min).
allowed-tools: Bash, Task, Agent, Read, Write
---

# /review-pr-parallel — Parallel PR review orchestrator (Lab 7)

## Step 1 — Get the diff

```bash
git diff main...HEAD --name-only
```

Collect the changed file list. If empty, tell the user there is nothing to review and stop.

## Step 2 — Dispatch all 5 reviewers in parallel

Use the Agent tool to launch all 5 simultaneously in a single response. Do NOT wait for one before starting the next:

```
Agent(style-cop,         "Review these files for style violations: <file list>")
Agent(contract-cop,      "Review these files for contract drift: <file list>")
Agent(lib-extractor,     "Review these files for shared-library extraction opportunities: <file list>")
Agent(test-quality,      "Review these files for test quality issues: <file list>")
Agent(security-reviewer, "Review these files for security vulnerabilities: <file list>")
```

Wait for ALL five to complete before proceeding to Step 3.

## Step 3 — Synthesize verdict

- Any **Critical** from `security-reviewer` → **BLOCKED**
- Any **Critical** from other reviewers → **CONDITIONAL**
- Zero Criticals from all 5 → **APPROVED**

## Step 4 — Emit report

Same format as /review-pr. Write to `reviews/<branch>-parallel.md`.

```
## /review-pr-parallel — <branch> → main

### Style cop
[findings or "✓ No critical violations"]

### Contract cop
[findings or "✓ No critical violations"]

### Shared-lib extractor
[findings or "✓ No extraction opportunities found"]

### Test quality
[findings or "✓ No critical issues"]

### Security reviewer
[findings or "✓ No critical vulnerabilities"]

---
**Verdict: APPROVED / CONDITIONAL / BLOCKED**
[One sentence. Note: parallel run — ~Xs wall-clock.]
```
