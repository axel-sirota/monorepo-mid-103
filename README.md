# monorepo-example

A runnable polyglot SaaS demo used by **Salesforce Course 102 and Course 103**. Models a small internal product: an ML-powered churn-risk emailer.

> **You are at the INITIAL stage.** The product works. The Claude Code extension layer (agents + skills + hooks + review pipeline + cost telemetry + Agent Teams) is **what we build together in 102 and 103**. Nothing in `.claude/` is pre-shipped.

## What's inside

```
monorepo-example/
├── apps/                       # engineer cluster
│   ├── api-gateway/            # Java 21 / Spring Boot 3 / Maven
│   ├── user-service/           # Python 3.12 / FastAPI / uv
│   └── notification-service/   # Go 1.22 / Gin / sqlx
├── ml/                         # data-scientist cluster
│   ├── model-serving/          # FastAPI + scikit-learn
│   ├── training/               # one-shot trainer + MLflow
│   └── inference-gateway/      # Go Gin proxy with API key + rate limit
├── frontend/                   # designer cluster
│   ├── design-tokens/          # Style Dictionary v5
│   ├── component-library/      # Vite + React 19 + TypeScript
│   └── docs-site/              # Storybook 8
├── infra/                      # devops cluster
│   ├── terraform/              # local-stub terraform
│   └── docker/postgres-init/   # initial database creation
├── prds/                       # pm cluster (PRDs in Markdown)
├── contracts/                  # shared (JSON Schema today; OpenAPI by end of 103)
├── personas/                   # persona packs installed by /set-persona
└── materials/                  # 102 + 103 decks and labs
```

## Run it

You need Docker Desktop. That's it.

```bash
cp .env.example .env
make up
```

Wait ~60 seconds for everything to come up healthy. Then:

```bash
make train             # trains the churn model and writes the joblib
make predict           # sample prediction request
make logs              # tail logs across all services
```

Hit:
- `http://localhost:8080/health` — api-gateway
- `http://localhost:8001/docs` — user-service OpenAPI UI
- `http://localhost:8002/health` — notification-service
- `http://localhost:9000/health` — inference-gateway
- `http://localhost:9001/health` — model-serving
- `http://localhost:8025` — Mailhog UI (dev SMTP catch-all)
- `http://localhost:5000` — MLflow UI

Stop with `make down`. Wipe state with `make reset`.

## Develop in one service

Each service has its own README with standalone run instructions (no Docker needed if you have the language toolchain locally).

For hot reload across the full stack:

```bash
make up-dev
```

## Test

```bash
make test              # everything
make test-apps         # Java + Python + Go in apps/
make test-ml           # Python + Go in ml/
make test-frontend     # vitest in frontend/
```

## Class-time orientation

| You're here | Read this |
| ----------- | --------- |
| Day 1, Course 102 | `materials/102/instructor-notes.md` for the instructor; `materials/102/labs/102-lab-1-subagents.md` for the first lab |
| Day 1, Course 103 | `materials/103/instructor-notes.md`; `materials/103/labs/103-lab-1-review-pipeline.md` |
| Just here exploring | `prds/0001-churn-notification.md` (the seed feature) and the per-service READMEs |

## Course flow at a glance

- **102** turns this raw monorepo into a *scoped, parallel, guard-railed* dev environment by adding subagents, skills, and hooks per persona.
- **103** takes the 102 output and makes it *production-grade*: parallel review pipeline, cost telemetry + model routing, Agent Teams for cross-service work, and a contracts migration from JSON Schema to OpenAPI with codegen.

Read `CLAUDE.md` for the architecture overview Claude itself sees.

## Prerequisites for local dev (outside Docker)

| Language   | Version | Why |
| ---------- | ------- | --- |
| Docker     | 25+     | Required for `docker compose`. Everything else is optional. |
| Java       | 21      | Only if you want to run api-gateway outside Docker (`mvn spring-boot:run`) |
| Python     | 3.12    | Only if you want to run Python services outside Docker |
| `uv`       | latest  | Python dep manager (`brew install uv` or `pip install uv`) |
| Go         | 1.22+   | Only if you want to run Go services outside Docker |
| Node       | 20+     | Only if you want to run frontend outside Docker |

## License

Internal training material. Not for redistribution.
