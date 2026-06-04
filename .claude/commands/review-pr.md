---
name: review-pr
description: Orchestrate a full craft review of the current PR diff. Dispatches style-cop, contract-cop, lib-extractor, test-quality, and security-reviewer in sequence. Emits APPROVED / CONDITIONAL / BLOCKED verdict.
allowed-tools: Bash, Task, Read, Write
---

# /review-pr — PR review orchestrator (sequential)

## Step 1 — Get the diff

```bash
git diff main...HEAD --name-only
```

Collect the changed file list. If empty, tell the user there is nothing to review and stop.

## Step 2 — Run all 5 reviewers in sequence

Dispatch each agent via Task in this order, waiting for each to complete before starting the next:

1. `Task(style-cop, "Review these files for style violations: <file list>")`
2. `Task(contract-cop, "Review these files for contract drift: <file list>")`
3. `Task(lib-extractor, "Review these files for shared-library extraction opportunities: <file list>")`
4. `Task(test-quality, "Review these files for test quality issues: <file list>")`
5. `Task(security-reviewer, "Review these files for security vulnerabilities: <file list>")`

## Step 3 — Synthesize verdict

- Any **Critical** from `security-reviewer` → **BLOCKED**
- Any **Critical** from other reviewers → **CONDITIONAL**
- Zero Criticals from all 5 → **APPROVED**

## Step 4 — Emit report

```
## /review-pr — <branch> → main

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
[One sentence explaining the verdict]
```

Write the report to `reviews/<branch>.md`.
