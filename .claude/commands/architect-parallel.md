---
name: architect-parallel
description: Parallel architecture implementation using git worktrees for isolation. Analyzes a feature, identifies which service changes are independent, sets up a worktree per service, dispatches subagents in parallel, then merges. Use when implementing a cross-service feature where service changes don't depend on each other.
allowed-tools: Bash, Agent, Read, Write, Task
---

# /architect-parallel — Parallel cross-service implementation with worktree isolation

## When to use this vs normal implementation

Use this command when ALL of the following are true:
1. The feature touches **2+ services** (e.g. user-service + notification-service + api-gateway)
2. The per-service changes are **independent** — service A's implementation doesn't depend on service B finishing first
3. The changes are **scoped to one service directory** each — no two subagents write to the same file

Do NOT use this when:
- One service must be implemented before another can be (sequential dependency)
- Changes span shared files like `contracts/schemas/` (shared write → race condition)
- The feature is small enough that sequential is faster than worktree setup overhead

## Step 1 — Analyze the feature

Read the relevant PRD or user request. Identify:
- Which services need changes
- Whether changes are independent or sequential
- Which files each service change touches

Output a dependency table:

```
Service          | Files touched                      | Depends on
─────────────────┼────────────────────────────────────┼───────────
user-service     | app/api/users.py, app/schemas/     | nothing
notification-svc | internal/handler/notify.go          | nothing
api-gateway      | controller/UserController.java      | user-service (needs its endpoint URL)
```

If any service depends on another → implement those in sequence first, then parallelize the rest.

## Step 2 — Update shared contracts first (sequential, always)

If the feature requires schema changes in `contracts/schemas/` or `contracts/openapi/`, do those FIRST in the main worktree before spinning up parallel workers. Schema is shared — it cannot be split.

```bash
# Edit contracts/schemas/user.json or contracts/openapi/user.yaml
# Commit the schema change on a feature branch
git checkout -b feat/<feature-slug>
git add contracts/
git commit -m "contracts: add <field> for <feature>"
```

## Step 3 — Set up one worktree per independent service

For each independent service, create an isolated worktree:

```bash
# user-service worktree
git worktree add ../worktree-user-service feat/<feature-slug>

# notification-service worktree
git worktree add ../worktree-notification-svc feat/<feature-slug>
```

Each worktree is on the same branch, fully isolated on disk. Subagents write to their worktree only.

## Step 4 — Dispatch subagents in parallel

Launch one agent per service simultaneously using the Agent tool:

```
Agent(engineer-apps, "Implement <feature> in apps/user-service/ inside worktree at ../worktree-user-service. Context: <schema change summary>. Only touch files under apps/user-service/.")

Agent(engineer-apps, "Implement <feature> in apps/notification-service/ inside worktree at ../worktree-notification-svc. Context: <schema change summary>. Only touch files under apps/notification-service/.")
```

Each agent:
- Works in its own worktree directory
- Has no awareness of the other agents
- Commits its own changes to the feature branch

Wait for ALL agents to complete before Step 5.

## Step 5 — Merge worktrees back

After all agents complete, merge each worktree's commits:

```bash
# Review what each worktree produced
git log feat/<feature-slug> --oneline --graph

# Clean up worktrees
git worktree remove ../worktree-user-service
git worktree remove ../worktree-notification-svc
```

The feature branch now has all service changes from all agents.

## Step 6 — Run /review-pr-parallel

```
/review-pr-parallel
```

All 5 craft agents review the full diff in parallel. Expected: the schema update, all service implementations, and tests pass the review gate.

## Step 7 — Announce the dependency order

At the end, output a clear summary:

```
## Implementation order

Sequential (done first):
  1. contracts/schemas/user.json — schema source of truth

Parallel (done simultaneously):
  2a. apps/user-service/ — <agent 1 summary>
  2b. apps/notification-service/ — <agent 2 summary>

Sequential (done after parallel):
  3. apps/api-gateway/ — depends on user-service endpoint being defined

Total wall-clock: ~Xs (vs ~Xs sequential)
```

## Worktree rules

- Each worktree gets **one agent** — never share a worktree between agents
- Agents must **only write inside their assigned service directory**
- **Contracts and shared files** always stay in the main worktree and are committed first
- Run `/review-pr-parallel` from the main worktree after cleanup, not from a worktree
