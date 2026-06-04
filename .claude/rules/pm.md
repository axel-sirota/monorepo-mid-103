---
paths:
  - "prds/**/*.md"
---

# PRD authoring rules (path-scoped)

Loaded by Claude only when files matching `prds/**/*.md` are in context. Adds to the root `CLAUDE.md` for PRD-shaped work.

## Template-first

Every PRD starts from `prds/_template.md` and fills every section. Do not delete sections — if a section is genuinely N/A, write `N/A — <one-line reason>` instead.

## INVEST stories

Every user story must be:

- **Independent** — can ship without other stories in the same PRD. List `Depends on:` when you can't avoid it.
- **Negotiable** — describes intent, not implementation. No "use a Postgres trigger" in the story body.
- **Valuable** — the **So that** clause is a real outcome for a real user. "So that we have feature parity" is NOT valuable.
- **Estimable** — small enough that an engineer can ballpark it in story points without re-asking what it means.
- **Small** — fits in one sprint. If it doesn't, split it.
- **Testable** — every story has at least one Given/When/Then acceptance criterion.

## Given/When/Then acceptance criteria

Every AC is exactly one Given/When/Then triple on a single bullet:

- **Given** `<precondition>`, **When** `<action>`, **Then** `<observable outcome>`.

No "Given X and Y" lists — split into two ACs. No "Then it works correctly" — name the observable behaviour (status code, body shape, log line, side effect).

## NFRs are explicit

Section 4 must populate at least four of: **Performance**, **Security**, **Observability**, **Reliability**, **Cost**, **Privacy/Compliance**, **Accessibility** (the last only if UI is touched). Each populated subsection has a numeric or otherwise testable claim — not prose hand-waves.

## Contracts cross-reference

If a PRD changes or extends a service's request/response shape, list the affected file(s) in the front-matter `Contracts:` field and link them inline in the relevant story. If a new shape is being added (e.g. `UserExport`), the PRD names the new `contracts/schemas/<name>.json` file even if it doesn't yet exist — the engineer subagent creates it from the PRD.

## Forbidden in committed PRDs

- `TODO`, `TBD`, or `??` placeholders in the body. (HTML-comment `<!-- TODO -->` lines are exempt — they're for drafts.)
- "Out of scope: TBD" — pick at least one explicit exclusion or write "Nothing is out of scope for v1" and own it.
- Inventing contract fields. Reference real fields from `contracts/schemas/*.json` or propose a new schema explicitly.

The `pm-check` pre-commit hook enforces a subset of these (story heading, G/W/T triple, NFR section, forbidden tokens). The rest are honoured by the `pm-prds` subagent.
