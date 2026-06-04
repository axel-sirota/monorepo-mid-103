
# libs/ — Shared Libraries

Shared libraries extracted from services. Each subdirectory is a language-neutral module with per-language implementations.

This directory starts empty. In Lab 3 (shared-library extraction), the `lib-extractor` agent detects cross-service code duplication and extracts it here.

## Structure (after Lab 3)

```
libs/
├── go-common/          # Extracted Go middleware (request_id, logger, config)
│   ├── go.mod
│   └── middleware/
└── ...                 # Other extracted libs added by subsequent labs
```

## Adding a new library

1. Run the `lib-extractor` agent (`.claude/agents/lib-extractor.md`) on the target cluster.
2. Review the extraction plan.
3. Run `/extract-shared` to scaffold the library and update consumer imports.
