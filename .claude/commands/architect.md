---
description: Phase 0 — design + scaffold session plans, driven by .claude/pipeline.yaml
---

# /architect — persona-agnostic planning command

This command reads `.claude/pipeline.yaml` to know which persona is installed
and what artifacts to produce. The persona's `architect_output` block decides
where session files land. The persona's `scope` decides what the interface
contract is allowed to touch. **No persona prose branching** — pipeline.yaml
is the contract.

Three gated phases:
1. **Design** — produce planning docs (interface contract + session files).
2. **⛔ Human Review** — student reads and approves before any code lands.
3. **Scaffold** — write the per-session files under the persona's `sessions_dir`.

---

## Step 0 — Read pipeline.yaml first

```bash
test -f .claude/pipeline.yaml || { echo "no persona configured — run /set-persona first or cp personas/<persona>/pipeline.yaml .claude/"; exit 1; }
```

Read `.claude/pipeline.yaml`. Pull out:
- `persona` → drives the interface-shape preamble below.
- `scope.paths_allowed` / `scope.paths_denied` → reject session goals that
  obviously land outside scope.
- `architect_output.plans_dir`, `architect_output.sessions_dir`,
  `architect_output.interface_contract` → where files land.

If pipeline.yaml is missing or malformed, FAIL with:
> "pipeline.yaml missing or invalid — copy from personas/<persona>/pipeline.yaml. /architect cannot proceed without a persona contract."

## Step 1 — Persona-shaped interface preamble

Pick the interface shape from `persona`:

| persona | interface artifact |
|---|---|
| `engineer` | REST routes (method + path + request/response shape, referencing `contracts/schemas/*.json`) |
| `designer` | Component tree (existing vs. new), token requirements, layout structure |
| `pm` | PRD structure — goals, non-goals, personas, INVEST stories, NFR sections |
| `data-scientist` | Experiment plan — data sources, hypotheses, candidate models, metrics |
| `devops` | Module inputs/outputs, resource map, plan-out file naming |

## Step 2 — Plan source detection

Check whether the user provided a plan document (file path, pasted content,
or one of `plan.md` / `requirements.md` / `PRD.md` exists). Plan found →
Extraction Mode (trust the plan; ask if ambiguous). No plan → Design Mode
(design the persona's interface shape from Step 1).

---

## ══════════════════════════════════════
## PHASE 1 — DESIGN DOCS
## ══════════════════════════════════════

Goal: produce all planning artifacts. **No code, no scaffold, no cluster edits.**

Before creating any file, PRINT the manifest:

```
ARCHITECT OUTPUT MANIFEST
=========================
persona:           <from pipeline.yaml>
plans_dir:         <architect_output.plans_dir>
sessions_dir:      <architect_output.sessions_dir>
interface_contract: <architect_output.interface_contract>

I will create:
  - <interface_contract>                       ← <one-line description>
  - <sessions_dir>session-overview.md          ← phase breakdown + session list
  - <sessions_dir>session-1-<slug>.md          ← first session
  - <sessions_dir>session-N-<slug>.md          ← additional sessions
```

Then write each file. Session file format:

```markdown
# Session N: <Title>

## Goal
<one sentence>

## Scope (from pipeline.yaml)
- Allowed: <paths_allowed>
- Denied:  <paths_denied>

## Tasks
- [ ] <concrete task>
- [ ] <concrete task>

## Acceptance Criteria
- [ ] <verifiable outcome>

## Completion check (from pipeline.yaml)
`<completion_check.command>` must exit <expect_exit>.
```

📋 Print when Phase 1 done:
```
📋 PHASE 1 COMPLETE — Design docs written
   ✅ <interface_contract>
   ✅ <sessions_dir>session-overview.md
   ✅ <sessions_dir>session-1-<slug>.md
   ✅ <sessions_dir>session-N... ([N] total)
```

---

## ══════════════════════════════════════
## ⛔ PHASE 2 — HUMAN REVIEW GATE
## ══════════════════════════════════════

Print EXACTLY this and STOP. Do not write code. Do not scaffold:

```
⛔ REVIEW REQUIRED — No implementation yet. This is intentional.

Please review the planning docs:
  📂 <interface_contract>   — full interface design
  📂 <sessions_dir>         — [N] session files

Questions:
  • Does the interface match what you want?
  • Are features missing? Any you don't need?
  • Do session files break work into reasonable chunks?

To modify: edit any file in <plans_dir> directly and tell me what changed.

When satisfied, say: "approved" / "looks good" / "proceed".
```

Wait for explicit approval. Acceptable signals: "approved", "looks good",
"proceed", "ok go ahead", "yes", "lgtm", "build it". If the student asks for
changes, make them in the plans/ files, re-print the gate, wait again.

---

## ══════════════════════════════════════
## PHASE 3 — SCAFFOLD (after approval only)
## ══════════════════════════════════════

Scaffold the persona's first session walking skeleton inside
`scope.paths_allowed` ONLY. For engineer/designer/data-scientist/devops:
stub the entrypoint and any referenced module/component/route returning a
placeholder. For pm: nothing to scaffold — PRDs ARE the artifact; print
"PM has no skeleton phase — session files are the deliverables."

Confirm the scaffold parses/runs where applicable (e.g. `terraform validate`
for devops, `make test-apps` smoke for engineer, `npm run build:tokens` for
designer, `make test-ml` smoke for data-scientist).

📋 Print when Phase 3 done:
```
📋 PHASE 3 COMPLETE — Skeleton built
   ✅ Directory structure scaffolded inside scope.paths_allowed
   ✅ Stubs created
   ✅ Skeleton verified (parses / smoke test runs)
```

---

## Mandatory completion gate

Before printing the final summary, run:

```bash
ls <sessions_dir>
test -f <interface_contract>
```

Confirm the session-overview file + ≥1 session file + interface contract
exist. If any are missing, create them now.

Then print:

```
✅ /architect complete

Persona:  <persona> (from pipeline.yaml)
Plans:    <interface_contract> + N session files in <sessions_dir>

Next: /start-session to begin session 1.
```

---

## Key rules

- pipeline.yaml is the contract. Don't branch on persona name in prose;
  read fields.
- Never skip Phase 2. Approval is the gate.
- Never scaffold outside `scope.paths_allowed`.
- Never print the final ✅ without confirming files exist via `ls`.
