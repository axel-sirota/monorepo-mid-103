# monorepo-example — Project Context

> **Stage:** MID (starting state for Course 103)
>
> This is the starting state for Course 103. Students clone this repo and build 4 craft agents + `/review-pr` capstone.
>
> This is a runnable polyglot SaaS demo: an internal tool that emails users when an ML model predicts they're about to churn. It works today. In Course 103 you add the craft agents + skills + hooks layer: style consistency, API contract compliance, shared-library extraction, test quality, and a `/review-pr` orchestrator that composes all four.
>
> The agents/skills/hooks infrastructure from Course 102 is already present in `.claude/`. You are building ON TOP of it — not starting from scratch.

## The product, in one diagram

```
            ┌──────────────────┐
   API ───▶ │   api-gateway    │  (Java / Spring Boot)  :8080
            └────────┬─────────┘
                     │
       ┌─────────────┴──────────────┐
       ▼                            ▼
┌──────────────┐           ┌──────────────────────┐
│ user-service │           │ notification-service │
│ (Python/Fast │           │ (Go / Gin)           │
│  API) :8001  │           │  :8002 → Mailhog     │
└──────┬───────┘           └──────────────────────┘
       │
       ▼ HTTPS + API key
┌─────────────────────┐         ┌──────────────────┐
│ inference-gateway   │ ──────▶ │  model-serving   │
│ (Go / Gin) :9000    │         │  (Python/sklearn)│
└─────────────────────┘         │      :9001       │
                                └────────▲─────────┘
                                         │
                                ┌────────┴─────────┐
                                │     training      │
                                │  (one-shot) +     │
                                │     MLflow        │
                                └───────────────────┘
```

## Clusters and who owns them

| Cluster      | Persona         | Stack                                   |
| ------------ | --------------- | --------------------------------------- |
| `apps/`      | engineer        | Java Spring / Python FastAPI / Go Gin   |
| `ml/`        | data-scientist  | Python sklearn + MLflow / Go Gin proxy  |
| `frontend/`  | designer        | Style Dictionary + Vite/React + Storybook |
| `infra/`     | devops          | Terraform                               |
| `prds/`      | pm              | Markdown PRDs (INVEST + Given/When/Then)|
| `contracts/` | shared          | JSON Schema (source of truth for API shapes; will evolve to OpenAPI in Lab 6) |
| `libs/`      | shared          | Extracted shared libraries (scaffold present; populated in Lab 3) |

## Run it

```bash
cp .env.example .env
make up              # full stack
make train           # train the churn model (one-shot)
make predict         # sample prediction through inference-gateway
make logs            # tail everything
make down            # stop
make reset           # stop + wipe volumes
```

## Tests, lint, deps

```bash
make test            # all clusters
make lint            # all clusters
make install         # sync dependencies in all clusters
```

Per-cluster targets exist too: `test-apps`, `test-ml`, `test-frontend`, etc. See `make help`.

## Conventions

- **Contracts are the source of truth** for shapes that cross service boundaries. Today they live in `contracts/schemas/*.json` and are **hand-typed** in every service. They WILL drift. Solving that drift is what Lab 2 (contract compliance) is about.
- **Each service is self-contained**: own Dockerfile, own build config (pom.xml / pyproject.toml / go.mod / package.json), own README explaining how to run it standalone.
- **`make`-first**: every common task has a Makefile target. If you find yourself typing a long command twice, add it to the Makefile.
- **No build tool over the polyglot layer** (no Bazel/Nx/Turborepo) — `docker compose` is the orchestrator, `make` is the task runner.

## What's already here (from Course 102)

| Layer | What exists |
| ----- | ----------- |
| `.claude/agents/` | Persona-scoped subagents (engineer, pm, data-scientist, designer, devops) |
| `.claude/skills/` | Repeated-procedure skills per persona |
| `.claude/hooks/` | Commit-time hooks wired to each persona's cluster |
| `.claude/commands/` | Slash commands (e.g. `/set-persona`, `/start-session`) |
| `.claude/rules/` | Per-stack style rubrics (fastapi, spring, go-gin, typescript) |
| `contracts/schemas/` | JSON Schema source-of-truth (user, notification, prediction) |

## What you build in Course 103 (craft agents layer)

| Lab | What you build |
| --- | -------------- |
| Lab 1 — Style | `agents/style-cop.md` + `skills/enforce-style/` + `hooks/style-check.sh` |
| Lab 2 — Contract | `agents/contract-cop.md` + `skills/validate-contracts/` + `hooks/contract-check.sh` |
| Lab 3 — Shared-lib | `agents/lib-extractor.md` + `skills/extract-shared/` + `hooks/shared-lib-check.sh` + `libs/` cluster |
| Lab 4 — Test quality | `agents/test-quality.md` + `skills/measure-test-quality/` + `hooks/test-quality-check.sh` |
| Lab 5 — Capstone | `agents/security-reviewer.md` + `commands/review-pr.md` (composes Labs 1-4 + security) |

The craft agents are CROSS-CUTTING — they operate on the whole monorepo, not a single persona's cluster. After Lab 5, `/review-pr` dispatches all five craft reviewers in parallel and emits a deterministic BLOCKED/CONDITIONAL/APPROVED verdict.

## Quick links

- `materials/102/` — Course 102 deck + labs + instructor notes
- `materials/103/` — Course 103 deck + labs + instructor notes
- `personas/` — persona packs (`/set-persona` installs them into `.claude/`)
- `prds/0001-churn-notification.md` — the seed PRD this monorepo implements
- `contracts/schemas/` — JSON Schema source-of-truth files (user, notification, prediction)
- `libs/` — shared libraries destination (Lab 3 extraction target)
