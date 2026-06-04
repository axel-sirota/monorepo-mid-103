# Figma context: {{FRAME_NAME}}

**Frame URL:** {{FRAME_URL}}
**Extracted:** {{DATE}} by `/extract-figma-frame`
**Target component:** {{COMPONENT_NAME}}
**Mode:** {{MODE}}  <!-- "live (Figma MCP)" or "mock fixture" -->

## Tokens used

{{TOKEN_TABLE}}

<!-- Example row format:
| Figma value | Project token | Status |
|---|---|---|
| `#1e40af` | `var(--color-primary)` | matched |
| `16px` | `var(--spacing-md)` | matched |
| `#ff00aa` | _(proposed: `--color-accent-pink`)_ | **NEW TOKEN NEEDED** |
-->

## Components needed

{{COMPONENT_LIST}}

<!-- Example:
### {{ComponentName}}

**Variants:** primary, secondary
**States:** default, hover, focus, disabled
**Props (inferred):**

```ts
type {{ComponentName}}Props = {
  variant?: "primary" | "secondary";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
};
```
-->

## Layout notes

{{LAYOUT_NOTES}}

<!-- Anything about flex direction, alignment, spacing rhythm, responsive
     behavior at 375 / 768 / 1440 px. -->

## Open questions

- [ ] Are the proposed NEW TOKENS approved? Names final?
- [ ] Any accessibility constraints not visible in the frame (focus order, aria labels)?
- [ ] Empty / loading / error states present in Figma, or to be designed in code?

## Hand-off checklist

- [ ] Resolve all **NEW TOKEN NEEDED** entries in `frontend/design-tokens/tokens/`
- [ ] Run `npm run build:tokens`
- [ ] Implement component in `frontend/component-library/src/{{ComponentName}}/`
- [ ] Add story to `frontend/docs-site/stories/{{ComponentName}}.stories.tsx`
- [ ] Verify at 375 / 768 / 1440 px breakpoints in Storybook
