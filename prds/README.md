# prds/

PRD authoring conventions for the PM persona.

## Rules

1. Every PRD uses the template at `_template.md`.
2. Every user story is **INVEST**: Independent, Negotiable, Valuable, Estimable, Small, Testable.
3. Every acceptance criterion is **Given / When / Then**.
4. NFRs (non-functional requirements) are explicit. Don't bury performance/security/observability assumptions in prose.
5. Every PRD that affects a service shape MUST cross-reference the corresponding `contracts/schemas/*.json` file.

## Numbering

`NNNN-kebab-case.md`. NNNN is a zero-padded sequence. Don't reuse numbers.

## Index

| #    | Title                          | Status                | Touches                                                 |
| ---- | ------------------------------ | --------------------- | ------------------------------------------------------- |
| 0001 | Churn risk notification        | implemented           | apps/, ml/, contracts/{notification,prediction,user}    |
| 0002 | Export user data (GDPR/CCPA)   | draft — needs PM work | apps/user-service (partial), contracts/user (extends)   |
