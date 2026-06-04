---
paths:
  - "apps/**/*.go"
  - "ml/**/*.go"
---

# Go style rules

## Line length
Maximum **100 characters** per line. Over 100 = Warning.

## Logging
Use `slog` (Go 1.21+) or `zerolog`. Never `fmt.Println`, `fmt.Printf`, `log.Println` in production. Bare print = Critical.

## Error handling
Wrap errors: `fmt.Errorf("op: %w", err)`. Never discard with `_`. Unwrapped returns = Warning.

## Context propagation
Every I/O function (DB, HTTP, file) must take `ctx context.Context` as first param. Missing = Warning.
