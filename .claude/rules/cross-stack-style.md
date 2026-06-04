# Cross-stack style rules (all languages)

These rules apply to every file regardless of language.

## Request ID propagation
Every HTTP endpoint handler must propagate `X-Request-ID`. Read from incoming request; include in all outbound calls and log lines. Missing = Warning.

## Error envelope
All error responses (4xx, 5xx) must use:
```json
{"error": {"code": "SCREAMING_SNAKE", "message": "Human text.", "request_id": "..."}}
```
Raw string error responses = Critical.

## No credentials in source
API keys, passwords, JWT secrets must never appear in source. Use environment variables. Any string matching `sk-`, `ghp_`, `AKIA`, or adjacent to `password`/`secret`/`token`/`key` field names = Critical.

## Log levels
DEBUG → fine-grained trace. INFO → normal operational events. WARN → recoverable anomalies. ERROR → failures requiring operator attention. Never ERROR for expected business errors.
