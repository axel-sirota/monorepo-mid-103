# @monorepo/design-tokens

Source-of-truth for design tokens. Built with Style Dictionary v5.

## Layout

```
tokens/        # primitive token JSON ($type/$value format)
build.mjs      # Style Dictionary v5 ESM build script
dist/          # generated — gitignored
  css/tokens.css   # :root { --color-primary: ...; ... }
  ts/tokens.js     # ESM exports
  ts/tokens.d.ts   # TypeScript declarations
```

## Build

```bash
npm run build   # writes dist/
npm run clean   # removes dist/
```

## Consuming

```ts
// CSS variables (recommended — what component-library uses)
import '@monorepo/design-tokens/tokens.css';

// Typed JS exports (for non-CSS contexts)
import { ColorPrimary, SpacingMd } from '@monorepo/design-tokens/tokens';
```
