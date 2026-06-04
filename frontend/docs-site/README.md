# @monorepo/docs-site

Storybook 8 site documenting `@monorepo/component-library` and the underlying `@monorepo/design-tokens`.

Stories use CSF 3.0 (`Meta` / `StoryObj` from `@storybook/react`). Tokens are documented via the `storybook-design-token` addon (v3, the version that supports Storybook 8).

## Commands

```bash
npm run storybook        # dev server on http://localhost:6006
npm run build-storybook  # static build into storybook-static/
```

The preview imports `@monorepo/design-tokens/tokens.css` so all components inside Storybook receive the real token variables.
