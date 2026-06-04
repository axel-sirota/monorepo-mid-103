---
paths:
  - "apps/**/*.java"
---

# Java style rules (api-gateway)

## Line length
Maximum **100 characters** per line. Over 100 = Warning.

## Controller return types
All `@RestController` methods must return `ResponseEntity<ApiResponse<T>>`. Returning `ResponseEntity<String>` or bare `String` = Critical.

## Logging
Use SLF4J with `@Slf4j`: `log.info("event: {}", value)`. Never `System.out.println`. Bare print = Critical.

## DTOs
Use Java `record` for request/response shapes. Field names match `contracts/schemas/*.json` (snake_case in JSON via `@JsonProperty`).
