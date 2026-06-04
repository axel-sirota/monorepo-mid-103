# Class Bug Reference — feat/class-bugs (Course 103)

> INSTRUCTOR ONLY — Do not share with students before lab completion.
> This file lists all 15 deliberate bugs seeded on this branch for craft-agent detection labs.

## Style Bugs (style-cop agent)

| # | File | What | Marker |
|---|------|------|--------|
| 1 | `apps/user-service/app/core/config.py` | Hardcoded hex colour constant `BANNER_COLOR = "#FF5733"` | class-bug-1 |
| 2 | `apps/notification-service/internal/handler/notify.go` | `fmt.Println(...)` instead of structured logger in error path | class-bug-2 |
| 3 | `apps/api-gateway/src/main/java/com/example/gateway/controller/NotifyProxyController.java` | `ResponseEntity.badRequest().body("invalid input: ...")` raw String instead of standard `{"error":...}` envelope | class-bug-3 |

## Contract Bugs (contract-cop agent)

| # | File | What | Marker |
|---|------|------|--------|
| 4 | `contracts/schemas/user.json` + `apps/user-service/app/schemas/user.py` | `export_url` field in JSON schema but absent from Pydantic `User` model | class-bug-4 |
| 5 | `apps/api-gateway/src/main/java/com/example/gateway/model/UserDto.java` | `Instant created_at` — snake_case Java field name instead of camelCase `createdAt` + `@JsonProperty` | class-bug-5 |
| 6 | `contracts/schemas/user.json` + `apps/notification-service/internal/model/user.go` | `export_url` field in JSON schema but absent from Go `User` struct | class-bug-6 |

## Shared-Lib Bugs (lib-extractor agent)

| # | File | What | Marker |
|---|------|------|--------|
| 7 | `apps/user-service/app/schemas/user.py`, `apps/api-gateway/.../UserDto.java`, `apps/notification-service/internal/model/user.go` | `User` shape (id/email/created_at/engagement fields) hand-typed in 3 services | class-bug-7 |
| 8 | `apps/user-service/app/services/user_service.py` + `apps/notification-service/internal/service/email_utils.go` | `validate_email` duplicated across Python and Go | class-bug-8 |
| 9 | `apps/user-service/app/services/user_service.py` + `apps/notification-service/internal/service/email_utils.go` | `format_date` / `formatDate` duplicated across Python and Go | class-bug-9 |

## Test Quality Bugs (test-quality agent)

| # | File | What | Marker |
|---|------|------|--------|
| 10 | `apps/user-service/app/services/user_service.py` | `calculate_export_size()` is a public function with no test | class-bug-10 |
| 11 | `apps/user-service/tests/unit/test_user_service.py` | `test_user_creation()` has no assert — always passes, proves nothing | class-bug-11 |
| 12 | `apps/user-service/tests/unit/test_user_service.py` | `test_add_positive()` asserts `result > 0` — mutation-weak (2*3=6>0 survives) | class-bug-12 |

## Security Bugs (security-reviewer agent)

| # | File | What | Marker |
|---|------|------|--------|
| 13 | `apps/user-service/app/core/config.py` | `SECRET_TOKEN = "sk-prod-abc123def456"` hardcoded in source | class-bug-13 |
| 14 | `apps/user-service/app/services/user_service.py` | `get_user_raw()` uses `f"SELECT * FROM users WHERE id = {user_id}"` — SQL injection | class-bug-14 |
| 15 | `apps/user-service/app/api/users.py` | `/users/admin/all` endpoint has no authentication dependency | class-bug-15 |

---

## Fix Guide (for solution branch)

- Bug 1: Move `BANNER_COLOR` to a CSS token or remove; use `Settings` for any runtime constants
- Bug 2: Replace `fmt.Println` with `log.Printf` or inject a structured `*slog.Logger`
- Bug 3: Return `Map<String,Object>{"error":...,"code":...}` via `GlobalExceptionHandler` or a typed `ErrorDto`
- Bug 4: Add `export_url: Optional[str] = None` to the Pydantic `User` model
- Bug 5: Rename to `createdAt` and add `@JsonProperty("created_at")`
- Bug 6: Add `ExportURL *string \`json:"export_url,omitempty"\`` to Go `User` struct
- Bug 7: Extract shared `User` contract to codegen or a shared package
- Bug 8: Extract `validateEmail` to `libs/validators/`
- Bug 9: Extract `formatDate` to `libs/time_utils/`
- Bug 10: Add `test_calculate_export_size` in `tests/unit/`
- Bug 11: Add `assert user.email == "test@test.com"` or similar
- Bug 12: Change `assert result > 0` to `assert result == 5`
- Bug 13: Remove `SECRET_TOKEN`; load from `Settings` / environment variable
- Bug 14: Use parameterized query: `text("SELECT * FROM users WHERE id = :uid")`, params `{"uid": user_id}`
- Bug 15: Add `current_user = Depends(get_current_user)` parameter to `admin_list_all_users`
