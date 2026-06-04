---
name: validate-contracts
description: Validate all contracts/schemas/*.json against their service implementations. Use when asked to check schema drift, validate contracts, or verify service compatibility before a merge.
allowed-tools: Read, Glob, Grep, Bash, Task
---

# Validate contracts across all services

## Step 1 — Enumerate contracts

```bash
ls contracts/schemas/*.json
```

## Step 2 — Dispatch contract-cop

```
Task(contract-cop, "Validate all contracts in contracts/schemas/ against their service implementations in apps/. For each contract, check all consumer files listed in your consumer map. Report every drift finding.")
```

Wait for the full report.

## Step 3 — Summarize and gate

- **Critical findings present** → output report then: "Schema drift detected. Fix the consumer-side implementation (or update the schema AND ALL consumers in the same commit) before merging."
- **No Critical findings** → output Warnings then: "All contracts in sync. No blocking drift found."

This skill does NOT auto-fix drift. Contract resolution requires a human decision about which side is the source of truth.
