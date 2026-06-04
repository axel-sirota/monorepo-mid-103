# @monorepo/component-library

React 19 + TypeScript component library, built with Vite 7 in library mode.

## Components

- `Button` — primary / secondary / ghost / danger variants, sm / md / lg sizes
- `Card` — titled / footer container
- `Input` — labelled input with hint + error states (accessible via `aria-describedby` / `aria-invalid`)
- `NotificationBanner` — info / warning / danger / success (the danger variant powers the churn-risk demo UI)

All styling is via CSS custom properties from `@monorepo/design-tokens`. No hardcoded colors, spacing, or radii.

## Commands

```bash
npm run build       # vite library build -> dist/
npm test            # vitest (jsdom + @testing-library/react)
npm run dev         # vite dev server (rarely useful for a library; prefer storybook)
```

## Consuming

```ts
import { Button, Card, NotificationBanner } from '@monorepo/component-library';
import '@monorepo/component-library/styles.css';
```

The styles import pulls in the design-tokens CSS variables and per-component styles.
