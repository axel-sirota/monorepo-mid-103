# Designer persona — pre-class setup

## Required

- Docker Desktop 25+
- Node 20+ (frontend/ work runs natively, not in Docker)
- Python 3 (used by the Lab 3 install-hook.py installer — ships with macOS;
  `apt-get install python3` on Linux)
- Claude Code CLI

## Strongly recommended

- Figma desktop app (the Figma MCP server connects to the local app)
- A Figma personal access token (Settings → Account → Personal access tokens)

## Pre-class warm-up

```bash
cd frontend
npm install
npm run dev --workspace=component-library
# open Storybook
npm run storybook --workspace=docs-site
```

Confirm Storybook loads at http://localhost:6006 and the Tokens page renders.
