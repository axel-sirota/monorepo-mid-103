# Mock Figma frame — `toast-frame`

Simulates the Figma MCP response for a "Toast" frame. Used when
`FIGMA_ACCESS_TOKEN` is not set or the user passes `mock` as the file key
to the `extract-figma-frame` skill (Course 102 Designer Lab 2).

Preview: `https://placehold.co/600x120/1e40af/ffffff?text=Toast`

```json
{
  "name": "Toast",
  "type": "FRAME",
  "absoluteBoundingBox": { "width": 600, "height": 120 },
  "layoutMode": "HORIZONTAL",
  "primaryAxisAlignItems": "SPACE_BETWEEN",
  "counterAxisAlignItems": "CENTER",
  "paddingLeft": 16,
  "paddingRight": 16,
  "paddingTop": 12,
  "paddingBottom": 12,
  "itemSpacing": 16,
  "cornerRadius": 8,
  "fills": [{ "type": "SOLID", "hex": "#1e40af" }],
  "children": [
    {
      "name": "Icon",
      "type": "VECTOR",
      "fills": [{ "hex": "#ffffff" }],
      "absoluteBoundingBox": { "width": 20, "height": 20 }
    },
    {
      "name": "Title",
      "type": "TEXT",
      "characters": "Notification",
      "style": {
        "fontFamily": "Inter",
        "fontWeight": 600,
        "fontSize": 16,
        "lineHeightPx": 24
      },
      "fills": [{ "hex": "#ffffff" }]
    },
    {
      "name": "Dismiss",
      "type": "TEXT",
      "characters": "×",
      "style": {
        "fontFamily": "Inter",
        "fontWeight": 400,
        "fontSize": 20,
        "lineHeightPx": 20
      },
      "fills": [{ "hex": "#ffffff" }]
    }
  ]
}
```

## Expected mapping outcome

A correct `extract-figma-frame` run in mock mode produces a context file
where:

- `#1e40af` → `var(--color-primary)` (exact)
- `#ffffff` → `var(--color-neutral-0)` (exact)
- `16px` padding/font → `var(--spacing-md)` / `var(--font-size-md)` (exact)
- `12px` padding → **NEW** (recommend `--spacing-sm-plus: 12px`)
- `font-weight 600` → `var(--font-weight-semibold)` (exact)
- `8px` radius → `var(--radius-md)` (exact)

Exactly ONE NEW token should appear in the "NEW tokens to add" section.
Every other Figma value should map to an existing token.
