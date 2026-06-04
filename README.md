# monorepo-mid-103

Starting state for **Salesforce Course 103 — Craft Agents on a Real Monorepo**.

> **Stage:** MID — the product works, the 102 agent+skill+hook layer is pre-installed. You build the **4 craft agents + `/review-pr` capstone** in Course 103.

---

## Prerequisites — install before class

| Tool | Install | Verify |
|---|---|---|
| Docker Desktop (≥ 4.x) | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) | `docker --version` |
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` | `claude --version` |
| OpenAPI Generator (Lab 6 only) | `npm install -g @openapitools/openapi-generator-cli` | `openapi-generator version` |

Docker Desktop needs at least **8 GB** of memory allocated (Settings → Resources → Memory).

---

## Getting started

```bash
git clone https://github.com/axel-sirota/monorepo-mid-103
cd monorepo-mid-103
cp .env.example .env
make up
```

Wait ~60 s for all services to come up healthy. Then verify:

```bash
curl http://localhost:8080/health    # api-gateway
curl http://localhost:8001/health    # user-service
curl http://localhost:8002/health    # notification-service
```

Open the course materials in your browser:
- `salesforce-103/materials/index.html` (your instructor will share this file)

---

## What's inside

```
monorepo-mid-103/
├── apps/
│   ├── api-gateway/            Java 21 / Spring Boot 3
│   ├── user-service/           Python 3.12 / FastAPI
│   └── notification-service/   Go 1.22 / Gin
├── ml/                         Python sklearn + MLflow + Go inference proxy
├── frontend/                   React 19 + Style Dictionary + Storybook
├── infra/                      Terraform (local stub)
├── contracts/
│   ├── schemas/                JSON Schema (source of truth — Lab 2 target)
│   └── openapi/                OpenAPI 3.0 spec (Lab 6 target)
├── libs/                       Shared library home — empty today, populated in Lab 3
├── prds/                       Markdown PRDs (0001-churn-notification, 0002-export-user-data)
└── .claude/
    ├── agents/                 Your 102 subagents + Lab 1-4 craft agents go here
    ├── skills/                 Your 102 skills + Lab 1-4 craft skills go here
    ├── hooks/                  Your 102 hooks + Lab 1-4 craft hooks go here
    ├── commands/               /review-pr capstone goes here (Lab 5)
    ├── rules/                  Style rule files go here (Lab 1)
    └── settings.json           Permissions + hook registration
```

---

## Lab overview

| Lab | What you build | Branch |
|---|---|---|
| Lab 1 — Style | `style-cop` agent + `/enforce-style` skill + `style-check.sh` hook | `feat/class-bugs` |
| Lab 2 — Contract | `contract-cop` agent + `/validate-contracts` skill + `contract-check.sh` hook | `feat/class-bugs` |
| Lab 3 — Shared-lib | `lib-extractor` agent + `/extract-shared` skill + `shared-lib-check.sh` hook + `libs/` | `feat/class-bugs` |
| Lab 4 — Test-quality | `test-quality` agent + `/measure-test-quality` skill + `test-quality-check.sh` hook | `feat/class-bugs` |
| Lab 5 — Capstone | `security-reviewer` agent + `/review-pr` command (composes Labs 1-4 + security) | `feat/class-bugs` |
| Lab 6 — Codegen | Instructor demo: live OpenAPI edit → `make codegen` → `/review-pr` on the diff | `main` |

For Labs 1–5, checkout the pre-seeded bug branch first:

```bash
git checkout feat/class-bugs
```

---

## Registering a hook (Lab 1–4 pattern)

After writing your hook script at `.claude/hooks/<name>.sh`, register it in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit:*)",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/style-check.sh"
          }
        ]
      }
    ]
  }
}
```

Repeat for each craft hook — add a new entry to the `hooks` array. The colon-star matcher (`Bash(git commit:*)`) is required; space-star (`Bash(git commit *)`) is broken (GH #36389).

---

## Common make targets

```bash
make up          # start full stack
make down        # stop
make reset       # stop + wipe volumes
make logs        # tail all services
make train       # train churn model (run once after make up)
make predict     # sample prediction
make test        # run all tests
make codegen     # regenerate OpenAPI stubs (Lab 6 — requires openapi-generator)
make help        # full target list
```

---

## Useful URLs (while stack is running)

| Service | URL |
|---|---|
| api-gateway | http://localhost:8080 |
| user-service docs | http://localhost:8001/docs |
| notification-service | http://localhost:8002/health |
| inference-gateway | http://localhost:9000/health |
| model-serving | http://localhost:9001/health |
| Mailhog (email UI) | http://localhost:8025 |
| MLflow UI | http://localhost:5000 |
