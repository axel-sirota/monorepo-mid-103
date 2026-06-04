# frontend/ — design system + docs cluster

Lazy-loaded by Claude Code when working with files under `frontend/`. The root `/CLAUDE.md` still loads first.

## The three workspaces

| Workspace | Stack | Ships |
|---|---|---|
| `design-tokens` | Style Dictionary v5 | `dist/css/tokens.css`, `dist/ts/tokens.ts` |
| `component-library` | React 19 + TypeScript + Vite 7 | `Button`, `Card`, `Input`, `NotificationBanner` |
| `docs-site` | Storybook 8 (+ `storybook-design-token`) | Live component playground + token catalog |

We use **npm workspaces** — no pnpm, no yarn. Node 20+ (pinned in `.nvmrc`).

## Tokens are the source of truth

A hardcoded hex code, rgb/hsl literal, or `px` value in a component file is a bug. Every visual property MUST reference a token via a CSS custom property exported by `@monorepo/design-tokens`.

### Naming convention (CSS custom properties)

The Style Dictionary build emits CSS custom properties using dot-to-dash flattening of the token JSON paths:

| Token JSON path | CSS variable |
|---|---|
| `color.primary` | `var(--color-primary)` |
| `color.neutral.0` | `var(--color-neutral-0)` |
| `color.danger` | `var(--color-danger)` |
| `spacing.md` | `var(--spacing-md)` |
| `radius.md` | `var(--radius-md)` |
| `typography.font-size.md` | `var(--font-size-md)` |
| `typography.font-weight.semibold` | `var(--font-weight-semibold)` |

Allowed exceptions where literal values are OK:
- `frontend/design-tokens/tokens/*.json` (the source itself)
- Test fixtures (`*.test.tsx`)
- Storybook control args / arg-types

Anywhere else, the `designer-check` pre-commit hook will block the commit.

## Storybook is the contract with engineers

Every shippable component in `component-library/src/` MUST have a matching story in `docs-site/stories/`. If it's not in Storybook, engineers can't see it, so it's not done.

## Responsive breakpoints

Components are visually verified at three widths:
- `375px` (mobile)
- `768px` (tablet)
- `1440px` (desktop)

Storybook viewports are preconfigured for these three.

## npm scripts (run from `frontend/`)

```bash
npm install                            # install all workspaces
npm run build:tokens                   # build design-tokens -> dist/
npm run build:components               # build component-library -> dist/
npm run build                          # both, in order
npm run storybook                      # launch Storybook dev on :6006
npm run build-storybook -w docs-site   # static Storybook build (smoke)
npm test --workspaces --if-present     # vitest in all workspaces that have tests
```

## Active subagent + skill + hook

- **Subagent** `designer-frontend` — scoped to this cluster. Use `@agent-designer-frontend` or let auto-routing pick it up when a frontend file is mentioned.
- **Skill** `/extract-figma-frame` — pulls tokens + component spec from a Figma frame (live MCP or the mock fixture) into `frontend/docs/figma-context-{slug}.md`.
- **Hook** `designer-check` — pre-commit; scans staged `.ts`/`.tsx`/`.css`/`.scss` files under `frontend/` for hex/px literals; blocks the commit if any are found.

## DO NOT

- Don't touch `apps/`, `ml/`, `infra/`, or `prds/` from inside a frontend task — escalate to the owning persona.
- Don't bypass the tokens system to ship "just this one color." It compounds.
- Don't add a 4th workspace without updating this file and `frontend/package.json`.

## Cross-cluster coordination

If a new component needs a backend field that doesn't exist yet (e.g. a new shape on `contracts/schemas/*.json`), that's an **Agent Teams** scenario — covered in Course 103. For 102, scope work strictly within `frontend/`.
