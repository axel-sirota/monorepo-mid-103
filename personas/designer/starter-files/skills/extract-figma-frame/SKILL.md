---
name: extract-figma-frame
description: Pull tokens and component spec from a Figma frame into docs/figma-context-{slug}.md. Supports live Figma MCP and a static mock-frame fallback. Use when the user provides a Figma frame URL or asks to extract from Figma.
allowed-tools: Read, Write, Bash, mcp__figma__get_file, mcp__figma__get_image
---

# Extract a Figma frame into a context file

You are extracting a Figma frame into a normalized context file that the
`designer-frontend` subagent can consume when building components.

## Step 1 — Get the input

Ask the user for ONE of:
- A Figma frame URL (live mode), OR
- A slug like `toast-frame` to use the static mock fixture (mock mode)

If they provide neither, STOP and ask — do not guess.

Also ask for a target component name if the frame represents a single component
(e.g. `Toast`, `NotificationBanner`). If they don't have one, infer one from the
frame name later.

## Step 2 — Decide live or mock

Check whether `FIGMA_ACCESS_TOKEN` is set in the environment:

```bash
test -n "${FIGMA_ACCESS_TOKEN:-}" && echo live || echo mock
```

- **Live mode** (`FIGMA_ACCESS_TOKEN` set and the user provided a URL): call the
  Figma MCP tools — `mcp__figma__get_file` for the node tree, then
  `mcp__figma__get_image` if you need screenshots.
- **Mock mode** (no token OR user asked for mock): read
  `materials/102/figma-mock-frame.md` and parse the JSON block inside. Tell the
  user clearly: "Using mock fixture — Figma MCP not configured."

> **Note:** The exact MCP tool names depend on the installed Figma MCP package
> (`figma-developer-mcp` or similar). If `mcp__figma__*` is not available in
> your toolset, treat it as mock mode and fall back to the fixture.

## Step 3 — Map raw Figma values to project tokens

Open `frontend/design-tokens/tokens/color.json`, `spacing.json`, `radius.json`,
`typography.json`. For each Figma value (colors, font sizes, weights, spacing,
radii):

- If the raw value matches an existing token exactly → record the CSS variable
  name (e.g. `#1e40af` → `var(--color-primary)`).
- If no token matches → record the raw value AND propose a token name following
  the project naming convention. Mark it **NEW TOKEN NEEDED** in the output and
  ask the user to confirm the proposed name before they add it to the JSON.

The mock fixture in `materials/102/figma-mock-frame.md` lists the expected
mapping outcome at the bottom — use it as a sanity check when running in mock
mode.

## Step 4 — Render the context file

Use the template at `${CLAUDE_SKILL_DIR}/templates/figma-context-template.md`.
Substitute the placeholders, then write the result to:

```
frontend/docs/figma-context-{slug}.md
```

where `{slug}` is a kebab-case derivative of the frame name.

Create the `frontend/docs/` directory if it doesn't exist.

## Step 5 — Print summary

Report to the user:
- Path to the new context file
- Total tokens referenced
- Count of **NEW TOKEN NEEDED** entries (and the proposed names)
- Implied implementation order: tokens (if any new) → component → story

## DO NOT

- Don't generate component code in this skill — the hand-off is the context file.
- Don't add tokens to `frontend/design-tokens/tokens/*.json` from inside this
  skill — write them as recommendations and let the user (or a follow-up
  designer-frontend invocation) commit the token change deliberately.
