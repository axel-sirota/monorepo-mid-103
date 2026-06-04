---
paths:
  - "apps/**/*.py"
  - "ml/**/*.py"
---

# Python style rules

## Line length
Maximum **88 characters** per line (Black default). Over 88 = Warning.

## Color tokens
Never hardcode hex strings (`"#FF5733"`). Import from `app.tokens` or `shared.tokens`. Hardcoded hex = Critical.

## Logging
Use `structlog`. Every log call must be structured: `log.info("event", key=value)`. Bare `print()` in production = Critical.

## Type hints
All public functions must have type annotations on parameters and return value. Missing = Warning.

## Imports
stdlib → third-party → local. No wildcard imports.
