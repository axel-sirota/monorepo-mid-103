---
name: decompose-epic
description: Run Three Amigos validation on a PRD by dispatching dev-perspective, qa-perspective, and gap-detector subagents in parallel, then aggregate findings into the PRD's Three Amigos Findings section.
allowed-tools: Read, Edit, Task
---

# decompose-epic

Use this skill when a PRD is large, hand-wavy, partial, or needs a structured second-opinion pass before commit. It runs a real Three Amigos critique — three named voices, dispatched concurrently, each with its own system prompt and output discipline.

## Mechanism — read this first

This skill is NOT a single critique that "wears three hats." It is a **parallel fan-out to three named subagents** dispatched in the SAME assistant turn via three Task tool calls. The three voices are:

- `pm-dev-perspective` — flags technical feasibility, downstream service dependencies, and effort estimates.
- `pm-qa-perspective` — hunts edge cases, concurrency races, auth expiry, i18n, a11y, error states.
- `pm-gap-detector` — audits structural completeness against `prds/_template.md` and `.claude/rules/pm.md`.

**The WOW moment of this skill is three subagents firing simultaneously in the tool log.** Keep them in one assistant turn. Do not serialise (one Task, await, next Task) — that defeats the entire mechanism, and the perspectives anchor on each other when serialised.

## Inputs

The user supplies a path to a PRD file, e.g. `prds/0002-export-user-data.md`. If they didn't, ask once — do not guess.

## Procedure

### Step 1 — Read the target PRD

Use the Read tool to load the full PRD file. Note the front-matter (`Status`, `Owner`, `Touches`, `Contracts`) and the section headings so the perspective subagents have full context.

### Step 2 — Dispatch the three perspectives IN PARALLEL

In a single assistant response, invoke the Task tool three times — once per subagent. The three Task calls MUST appear in the same response block. Use this exact pattern:

```text
Task(subagent_type="pm-dev-perspective",
     description="Dev critique of PRD <NNNN>",
     prompt="Review this PRD for technical feasibility: <full PRD content>. Respond ONLY in the structured Markdown format demanded by your system prompt. Be specific — name services and files.")

Task(subagent_type="pm-qa-perspective",
     description="QA critique of PRD <NNNN>",
     prompt="Review this PRD for edge cases: <full PRD content>. Respond ONLY in the structured Markdown format demanded by your system prompt. Be specific — name the input that triggers each edge case.")

Task(subagent_type="pm-gap-detector",
     description="Gap audit of PRD <NNNN>",
     prompt="Review this PRD for structural gaps: <full PRD content>. Respond ONLY in the structured Markdown format demanded by your system prompt. Tier findings as Critical / Warning / Suggestion.")
```

If you find yourself writing "let me dispatch the dev one first and then…" — STOP. The three calls go in the same turn. The parallelism is the entire point.

### Step 3 — Collect the three structured outputs

When all three subagents return, you will have three Markdown blocks. Keep them verbatim — do not re-summarise or paraphrase. Each perspective's wording is load-bearing.

### Step 4 — Append (or replace) the Three Amigos Findings section in the PRD

Open `${CLAUDE_SKILL_DIR}/templates/three-amigos-findings.md` for the section template. Build the final Markdown block by substituting:

- `{{DATE}}` → today's date in `YYYY-MM-DD`.
- The three placeholder subsections → the verbatim subagent outputs from Step 3.

Use the Edit tool to insert the block at the end of the PRD file. If a `## Three Amigos Findings` section already exists from a prior run, REPLACE it — never accumulate stale findings.

### Step 5 — Print a summary

In your reply to the user, list:

- Which section was added or replaced.
- Count of findings per perspective (e.g. "Dev: 4 concerns, QA: 7 edge cases, Gap-detector: 3 Critical / 2 Warning / 1 Suggestion").
- The single highest-priority finding to resolve first (usually a gap-detector Critical, but use judgement).
- Reminder to the user: "Resolve a finding by editing the PRD body, then delete that bullet from the Findings section. Re-run this skill to refresh."

## What this skill does NOT do

- It does NOT auto-resolve findings. The PM resolves them by editing the PRD body; re-running confirms.
- It does NOT modify any file other than the target PRD. If a finding requires a contract change, name the contract file in the finding and stop.
- It does NOT dispatch the perspectives serially. Parallel dispatch is the entire mechanism. One assistant turn. Three Task calls.

## If you have an INVEST story scaffold to add

If gap-detector flags a missing story, use `${CLAUDE_SKILL_DIR}/templates/story-template.md` as the scaffold for the new story. Hand it back to the PM to fill in — do not write story bodies for them inside this skill.
