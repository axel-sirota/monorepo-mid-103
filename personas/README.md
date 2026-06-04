# personas/

Five persona packs. A persona is a role + cluster + workflow. Pick yours with `/set-persona`.

| Persona          | Cluster        | What they ship                                      |
| ---------------- | -------------- | --------------------------------------------------- |
| `engineer`       | `apps/`        | Service code behind tests, contracts honoured       |
| `designer`       | `frontend/`    | Tokens + components + Storybook stories             |
| `pm`             | `prds/`        | PRDs with INVEST stories + Given/When/Then ACs      |
| `data-scientist` | `ml/`          | Reproducible experiments + model artifacts          |
| `devops`         | `infra/`       | Terraform modules + container/runtime config        |

## Pack layout

Every persona has the same shape. The contents differ.

```
personas/{role}/
├── persona.md           # mental model, vocabulary, workflow phases
├── README.md            # what this pack adds when /set-persona installs it
├── SETUP.md             # pre-class checklist for the student
├── .env.example         # env vars this persona needs (Figma token, Jira creds, etc.)
├── mcp.json             # default MCP servers (generic open source; client-config overrides)
└── starter-files/       # files /set-persona copies into .claude/ at install time
    └── .gitkeep         # populated across 102 and 103 labs — empty at INITIAL
```

`/set-persona` copies `starter-files/` into `.claude/`. At INITIAL stage, every persona's `starter-files/` is empty. Each 102/103 lab writes one file (agent, skill, hook) into `starter-files/` and reinstalls.

## Why this shape

So that when an instructor runs a class for a different mix of personas, they can drop any pack in or out without disturbing the others. And so a real Salesforce team adopting this framework can keep their own persona overlays in `client-config/personas/{role}/` without touching the base packs (same overlay system as Course 101).
