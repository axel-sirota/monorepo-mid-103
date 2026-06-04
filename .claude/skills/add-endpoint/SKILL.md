---
name: add-endpoint
description: Add a new REST endpoint TDD-style to one of the apps/ services. Reads the contract, writes a failing test, implements until green, refactors. Use when the user asks to add, expose, or implement an endpoint, route, handler, or controller in apps/.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, Task
---

# Add an endpoint, TDD-style

This skill adds a single REST endpoint to one of the three `apps/` services with a real failing test BEFORE any implementation lands.

## Step 1 — Confirm target

Ask the user (if not already obvious):

- **Which service?** `api-gateway`, `user-service`, or `notification-service`
- **Which endpoint?** HTTP method + path (e.g. `POST /users/{id}/preferences`)
- **What contract?** Which `contracts/schemas/*.json` describes the request/response shape

If any of those three are missing or ambiguous, STOP and ask. Do NOT guess.

## Step 2 — Read the contract

Open the matching schema in `contracts/schemas/`. If no schema describes the shape, escalate: contracts are owned cross-team. Do not invent a shape silently.

## Step 3 — Pick the template

| Service | Test framework | Template |
|---|---|---|
| `api-gateway` | JUnit 5 + MockMvc | `.claude/skills/add-endpoint/templates/test-template-spring.java` |
| `user-service` | pytest + httpx AsyncClient | `.claude/skills/add-endpoint/templates/test-template-fastapi.py` |
| `notification-service` | testing + testify + httptest | `.claude/skills/add-endpoint/templates/test-template-go.go` |

Read the matching template. It shows the structure the new test must follow. Replace the `{{ENDPOINT}}`, `{{METHOD}}`, `{{NAME}}` tokens.

## Step 4 — Write the failing test FIRST

Write the new test file in the service's test tree:

- Spring: `apps/api-gateway/src/test/java/com/example/gateway/controller/{Name}ControllerTest.java`
- FastAPI: `apps/user-service/tests/integration/test_{name}_api.py`
- Go: `apps/notification-service/internal/handler/{name}_test.go`

Test MUST assert real behavior (status code + body shape from the contract), not just "endpoint exists."

## Step 5 — Verify the test is RED via test-runner subagent

Dispatch the `test-runner` subagent to run ONLY the new test and report the failure mode. Example invocation:

```
Use the Task tool:
  subagent_type: "test-runner"
  description: "Run new endpoint test, expect RED"
  prompt: "Run the test at {path}. Report exit code, the failing assertion, and whether the failure is for the right reason (endpoint missing / not yet implemented). Do not implement anything."
```

If the test does NOT fail (e.g. you accidentally implemented first, or the test is tautological), STOP. The whole point of this skill is red-first.

## Step 6 — Implement the minimum endpoint code

Wire the route, handler, service, and (if needed) repository layer. Match the file layout the service already uses — don't introduce new patterns. Reference the path-scoped rule (`spring.md` / `fastapi.md` / `go-gin.md`) loaded for the service.

## Step 7 — Verify GREEN via test-runner

Dispatch `test-runner` again:

```
Use the Task tool:
  subagent_type: "test-runner"
  description: "Re-run endpoint test, expect GREEN"
  prompt: "Run the test at {path}. Report exit code and pass/fail summary. If failing, return the diff between expected and actual."
```

If still red, fix; don't commit red.

## Step 8 — Refactor and run the full service suite

Tighten naming, remove duplication, add comments only where they explain *why*. Then run the whole cluster suite once more:

```
make test-apps
```

## Step 9 — Summary

Print to the user:

- Endpoint path + HTTP method
- Files changed (paths)
- Test count (new tests added, total tests in service)
- Contract reference (which `contracts/schemas/*.json` defined the shape)
- Re-run command (the per-service test command)
