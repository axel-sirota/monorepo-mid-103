# contracts/

Shapes that cross service boundaries live here. **At the INITIAL stage**, contracts are plain JSON Schema and every consuming service hand-types them. They will drift. That drift is what motivates the contract-codegen migration we do at the end of Course 103.

## Today's layout (INITIAL)

```
contracts/
├── schemas/
│   ├── user.json          # consumed by user-service AND api-gateway
│   ├── notification.json  # consumed by notification-service AND api-gateway
│   └── prediction.json    # consumed by model-serving AND inference-gateway AND user-service
```

## Who consumes what

| Schema              | Consumer service        | Where the hand-typed copy lives                                  |
| ------------------- | ----------------------- | ---------------------------------------------------------------- |
| `user.json`         | user-service (Python)   | `apps/user-service/app/schemas/user.py`                          |
| `user.json`         | api-gateway (Java)      | `apps/api-gateway/src/main/java/.../model/UserDto.java`          |
| `notification.json` | notification-service    | `apps/notification-service/internal/model/notification.go`       |
| `notification.json` | api-gateway (Java)      | `apps/api-gateway/src/main/java/.../model/NotificationDto.java`  |
| `prediction.json`   | model-serving (Python)  | `ml/model-serving/app/schemas/prediction.py`                     |
| `prediction.json`   | inference-gateway (Go)  | `ml/inference-gateway/internal/model/prediction.go`              |
| `prediction.json`   | user-service (Python)   | `apps/user-service/app/services/inference_client.py`             |

## How we'll evolve this

| Stage   | Source of truth                | Codegen                                                                                |
| ------- | ------------------------------ | -------------------------------------------------------------------------------------- |
| INITIAL | `contracts/schemas/*.json`     | None — hand-typed                                                                      |
| MID     | same                           | Same. But persona subagents notice drift in code review.                               |
| END     | `contracts/openapi/*.yaml`     | Per-language: `openapi-generator-maven-plugin` (Java), `datamodel-code-generator` (Python), `oapi-codegen` (Go). A skill regenerates all three. A hook blocks commits if codegen wasn't re-run. |

**Note on OpenAPI version:** when we migrate at end of 103, we target **OpenAPI 3.0**, not 3.1, because `oapi-codegen` (Go) doesn't support 3.1 yet.
