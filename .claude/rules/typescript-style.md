---
paths:
  - "frontend/**/*.ts"
  - "frontend/**/*.tsx"
---

# TypeScript style rules (frontend)

## Line length
Maximum **100 characters** per line. Over 100 = Warning.

## No `any`
Never use `any`. Use `unknown` + type guard, or proper interface. `any` in new code = Critical.

## Design tokens
All colors, spacing, and typography from `@salesforce/design-system-react` or `tokens/`. Hardcoded hex = Critical.

## Async error handling
Every `async` function or `.then()` chain must have `.catch()` or `try/catch`. Unhandled rejections in production paths = Critical.
