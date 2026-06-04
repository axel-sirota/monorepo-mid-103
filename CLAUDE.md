# monorepo-example — Project Context

> **Stage:** INITIAL (start of Course 102)
>
> This is a runnable polyglot SaaS demo: an internal tool that emails users when an ML model predicts they're about to churn. It works today. Across Courses 102 and 103, we add the agents + skills + hooks layer that turns this into a scoped, parallel, guard-railed, cost-optimised AI development environment.
>
> If you're starting fresh: run `/set-persona` to pick your role.

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
| `contracts/` | shared          | JSON Schema (will evolve to OpenAPI in 103) |

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

- **Contracts are the source of truth** for shapes that cross service boundaries. Today they live in `contracts/schemas/*.json` and are **hand-typed** in every service. They WILL drift. Solving that drift is what 102 and 103 are about.
- **Each service is self-contained**: own Dockerfile, own build config (pom.xml / pyproject.toml / go.mod / package.json), own README explaining how to run it standalone.
- **`make`-first**: every common task has a Makefile target. If you find yourself typing a long command twice, add it to the Makefile.
- **No build tool over the polyglot layer** (no Bazel/Nx/Turborepo) — `docker compose` is the orchestrator, `make` is the task runner.

## What's NOT here yet (we build this together)

- Subagents scoped to each persona's cluster (`.claude/agents/`)
- Skills that codify each persona's repeated procedures (`.claude/skills/`)
- Hooks that block at `git commit` if the cluster's standards aren't met (`.claude/hooks/`)
- A parallel review pipeline (`/review-pr`) with persona-specific reviewers
- Cost telemetry + model routing (`opusplan`, per-command `model:` frontmatter)
- Contracts migrated to OpenAPI 3.0 with per-language codegen
- Agent Teams config for cross-service coordination

If any of those are already in `.claude/`, you're past INITIAL stage — check `materials/102/` or `materials/103/` for which lab built what.

## Quick links

- `materials/102/` — Course 102 deck + labs + instructor notes
- `materials/103/` — Course 103 deck + labs + instructor notes
- `personas/` — persona packs (`/set-persona` installs them into `.claude/`)
- `prds/0001-churn-notification.md` — the seed PRD this monorepo implements
