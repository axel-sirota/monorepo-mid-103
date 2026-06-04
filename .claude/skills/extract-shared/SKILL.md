---
name: extract-shared
description: Detect cross-language duplication across services and scaffold shared libraries in libs/. Use when asked to find duplication, extract shared code, or scaffold a shared library.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, Task
---

# Extract shared libraries from duplicated code

## Step 1 — Detect duplication

```
Task(lib-extractor, "Scan apps/user-service/app/services/, apps/notification-service/internal/service/, and apps/api-gateway/src/main/java/**/service/ for structurally duplicated functions or types across services. Report each duplicate.")
```

Wait for the report.

## Step 2 — Gate

If `SHARED-LIB: CLEAN` → tell the user no duplication found and stop.

## Step 3 — Scaffold extraction (for each duplicate found)

For each `[DUPLICATE]` finding:
1. Read both source files to understand the full implementation.
2. Create the shared library file under `libs/`:
   - Python → `libs/validators/python/{name}.py`
   - Go → `libs/validators/go/{name}.go`
3. Include the extracted implementation with a comment referencing the source services.
4. Tell the user which imports to update in each service (do NOT edit service files directly).

## Step 4 — Report

List what was created, what still needs manual import updates, and the next step for the student.
