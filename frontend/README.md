# frontend/

Three npm workspaces wired together to provide a design system + docs site for the monorepo.

## Workspaces

- **`design-tokens/`** — Style Dictionary v5 source-of-truth for colors, spacing, typography, radii. Builds to CSS custom properties + a typed TS module.
- **`component-library/`** — Vite 7 + React 19 + TypeScript library (Button, Card, Input, NotificationBanner). Consumes tokens via CSS variables. Vitest + Testing Library.
- **`docs-site/`** — Storybook 8 site that renders the components and documents the tokens (via `storybook-design-token` v3).

## Persona docs

See `personas/designer/` at the monorepo root for the designer-facing narrative.

## Commands

Run from this `frontend/` directory:

```bash
npm install                  # install all workspaces
npm run build:tokens         # build design-tokens -> dist/css + dist/ts
npm run build:components     # build component-library -> dist/
npm run build                # both of the above, in order
npm test                     # run vitest in all workspaces that have tests
npm run storybook            # launch Storybook dev server on :6006
```

## Requirements

- Node 20+ (`.nvmrc` pins 20)
- npm (workspaces; no pnpm/yarn)
