---
name: measure-test-quality
description: Measure test quality across the monorepo or a specific service. Detects hollow tests, mutation-weak assertions, and uncovered public functions. Use when asked to check test quality, measure coverage, or audit tests.
allowed-tools: Read, Glob, Grep, Bash, Task
---

# Measure test quality

## Step 1 — Identify scope

If the user gave a path (e.g. `apps/user-service`), scope to that directory. Otherwise scan all services.

## Step 2 — Dispatch test-quality agent

```
Task(test-quality, "Measure test quality for {scope}. Check for: (1) test functions with zero assertions, (2) mutation-weak assertions like 'assert result > 0', (3) public functions with no test. Report every finding.")
```

Wait for the full report.

## Step 3 — Show numbers

For each service in scope, show:
- Number of test functions found
- Number with zero assertions (Critical)
- Number with mutation-weak assertions (Warning)
- Public functions with no test (Critical if new, Warning if existing)

## Step 4 — Gate

- Critical findings → "TEST-QUALITY: BLOCKED. Fix hollow tests before committing."
- Warnings only → "TEST-QUALITY: WARNING. Tests pass but coverage is weak."
- Clean → "TEST-QUALITY: PASS."
