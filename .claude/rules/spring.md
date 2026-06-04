---
paths:
  - "apps/api-gateway/**/*.java"
---

# Spring Boot conventions (api-gateway)

Loaded when Claude reads any Java file under `apps/api-gateway/`. Engineer persona ships this in 102 lab 1.

## Runtime + build

- Java 21 (records, pattern matching, virtual threads where useful).
- Spring Boot 3.4.x. No Spring Boot 2.x patterns.
- Maven with the wrapper. Always `./mvnw`, never bare `mvn`. The wrapper is the contract.

## Package layout

```
com.example.gateway
├── controller   — @RestController, thin; validates input, delegates to service
├── service      — business logic; no HTTP/DB types in signatures
├── repository   — Spring Data JPA OR sqlx-style JdbcClient; never raw JDBC
├── model        — DTOs (Java records) + JPA entities (separate classes)
├── config       — @Configuration beans (security, JSON, RestClient, filters)
└── exception    — AppException hierarchy + @ControllerAdvice GlobalExceptionHandler
```

## DTOs

- Use Java `record` for request/response DTOs. No Lombok.
- Field names match `contracts/schemas/*.json`. JSON is snake_case; if the Java field is camelCase, map via Jackson `@JsonProperty`.

## Exceptions

- Throw subclasses of `AppException`. NEVER return `ResponseEntity<String>` from controllers — let `GlobalExceptionHandler` map exceptions to HTTP status codes uniformly.

## Outbound HTTP

- Use `RestClient` (NOT `RestTemplate`, which is in maintenance mode).
- Each downstream service has its own `*Client` class in `service/` or a dedicated `client/` subpackage.

## Tests

- `@WebMvcTest({Controller}.class)` for thin controller tests with `MockMvc`.
- Integration tests use Testcontainers + Spring's `@ServiceConnection` for Postgres — no manual datasource wiring.
- Test naming: `methodUnderTest_condition_expectedResult` (e.g. `createUser_whenEmailExists_returns409`).
- Run with `cd apps/api-gateway && ./mvnw -B test`.
