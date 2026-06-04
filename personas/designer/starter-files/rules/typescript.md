---
paths:
  - "frontend/**/*.ts"
  - "frontend/**/*.tsx"
  - "frontend/**/*.css"
  - "frontend/**/*.scss"
---

# TypeScript / React / CSS conventions (frontend/)

## Type strictness

- `strict: true` in every `tsconfig.json`. Never weaken it.
- Never use `any`. Use `unknown` and narrow with type guards.
- `type` aliases for unions; `interface` for object shapes.
- Every public component exports a `{ComponentName}Props` type alongside the component.

## Styling — tokens only

- **No hardcoded colors** in component CSS or `.tsx`. Use `var(--color-*)` from `@monorepo/design-tokens/tokens.css`.
- **No hardcoded spacing.** Use `var(--spacing-*)`.
- **No hardcoded typography** (font sizes, weights, line heights). Use `var(--font-size-*)`, `var(--font-weight-*)`, `var(--line-height-*)`.
- **No inline `style={{...}}`** in `.tsx`. Use CSS modules.
- The `tokens.css` import lives once at the workspace entry; components consume the cascade.

## Components

- Function components only (no class components).
- Each component in `src/{ComponentName}/` with:
  - `{Name}.tsx` — implementation
  - `{Name}.test.tsx` — unit + a11y tests
  - `{Name}.module.css` — scoped styles
  - `index.ts` — re-export

## Stories — required, not optional

- Every component in `component-library/src/` has a matching story in `docs-site/stories/{Name}.stories.tsx`.
- CSF 3.0 format (`Meta`, `StoryObj`).
- At minimum: a `Default` story + one per variant.

## Accessibility-first

- Semantic HTML (`<button>`, `<nav>`, `<main>`) over `<div role="...">`.
- Inputs use `aria-describedby` for hints/errors and `aria-invalid` on error.
- Toggleable buttons use `aria-pressed`; disclosure controls use `aria-expanded`.
- Test with `@testing-library/react` queries that prefer accessible roles (`getByRole`).

## Tests

- `vitest` + `@testing-library/react`. `jsdom` environment.
- One `.test.tsx` per component, colocated.
- Run via `npm test -w component-library`.
