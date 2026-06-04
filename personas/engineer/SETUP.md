# Engineer persona — pre-class setup

Do this once, before class.

## Required

- Docker Desktop 25+ running
- `git` 2.30+
- Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)

## Optional but recommended

If you want to run services outside Docker for tighter iteration:

- Java 21 (`brew install openjdk@21` on macOS)
- Python 3.12 + `uv` (`brew install uv` or `pip install uv`)
- Go 1.22+ (`brew install go`)

## Verify

```bash
docker --version
claude --version          # ≥ 2.1.32 for Agent Teams (Course 103 capstone)
```

## Pre-class warm-up

1. `git clone <this repo>`
2. `cp .env.example .env`
3. `make up && make train && make predict`
4. Confirm you get a JSON probability back.

If `make predict` doesn't return a probability, fix that before day 1. You'll be much happier.
