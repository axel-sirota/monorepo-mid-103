# PRD 0002 — Export user data (GDPR / CCPA)

**Status:** implemented
**Owner:** PM (you)
**Last updated:** 2026-05-27
**Touches:** apps/user-service (new endpoint + export worker), apps/api-gateway (proxy + rate limit), apps/notification-service (download-link email)
**Contracts:** `contracts/schemas/user.json` (referenced read-only), `contracts/schemas/user_export.json` (NEW — drafted alongside this PRD)

## 1. Why

EU and California users have a legal right to a copy of all personal data we hold about them (GDPR Art. 15, CCPA §1798.110). Today they email support, support emails engineering, and an on-call engineer runs ad-hoc SQL to dump rows into a CSV that they then attach to a reply email.

That workflow is slow (typical turnaround 5–14 days, well outside the GDPR Art. 12(3) one-month ceiling and uncomfortably close to it on busy weeks), expensive (each export costs ~45 min of engineering time), and risky (CSV-by-email leaks PII to whatever inbox processed the support ticket, with no audit trail). One missed request is a regulatory finding.

We need a self-service flow that lets a logged-in user request an export and receive a signed, expiring download link by email, with every step audited.

## 2. Success metrics

- **Median time-to-export (request → delivered email):** < 24 h. (Upper bound: 7 days; GDPR Art. 12(3) ceiling 30 days.)
- **Engineering touches per export:** 0 (today: 1 ad-hoc DB query + 1 email per request).
- **Compliance audit findings on data-export workflow:** 0 per quarter (baseline: 2 findings in 2025 H2).
- **P95 export job duration** (queued → file ready): < 6 h for users with < 100 k activity rows.
- **Download-link expiry compliance:** 100% of links expire within 72 h of issue (auditable in `notification_log`).

## 3. User stories

### Story A — Request export
**As a** logged-in user
**I want** to request a download of all my personal data
**So that** I can satisfy my regulator or move to a competitor without waiting on a human.

**Depends on:** none

#### Acceptance criteria

- **Given** a logged-in user with a valid session, **When** they `POST /api/users/me/export`, **Then** the response is HTTP 202 with `{ "request_id": "<uuid>", "status": "queued", "estimated_ready_at": "<ISO-8601>" }`.
- **Given** the same user has already requested an export in the last 24 h, **When** they `POST /api/users/me/export` again, **Then** the response is HTTP 429 with `{ "error": "rate_limited", "retry_after_seconds": <int> }` and no new job is enqueued.
- **Given** an anonymous request, **When** they `POST /api/users/me/export` without a session cookie or with an expired token, **Then** the response is HTTP 401 and nothing is logged to `export_request_log` (we do not leak existence of accounts).
- **Given** a queued export job completes, **When** the worker calls `notification-service`, **Then** the user receives an email containing a signed download URL valid for 72 h, single-use (HTTP 410 on second access), tied to the requesting user's email at request time.

### Story B — Format of the export
**As a** logged-in user receiving an export
**I want** the export in a structured, machine-readable format with all my data in one archive
**So that** I can either inspect it or hand it to another service without parsing custom files.

**Depends on:** Story A

#### Acceptance criteria

- **Given** a completed export job, **When** the user downloads the file, **Then** they receive a ZIP archive named `user-{id}-export-{YYYYMMDD}.zip` containing `manifest.json`, `profile.json` (matching `contracts/schemas/user.json`), `sessions.json`, `notifications.json`, and `README.md` describing each file.
- **Given** the user has zero activity rows in a category (e.g. no notifications), **When** they download the ZIP, **Then** the corresponding file is still present and is a valid empty JSON array `[]` (not omitted — completeness matters for legal review).
- **Given** the export contains the user's `engagement_score`, `days_since_login`, `sessions_last_30d`, `support_tickets_last_90d` from `contracts/schemas/user.json`, **When** the user opens `profile.json`, **Then** all eight User properties appear with their last-known values at job start time (snapshot semantics, not live).
- **Given** the `manifest.json`, **When** the user opens it, **Then** it lists every file in the ZIP with SHA-256 checksum, row count, and the snapshot timestamp, conforming to the new `contracts/schemas/user_export.json` schema.

### Story C — Operator audit trail
**As a** compliance operator
**I want** a tamper-evident record of every export request, who made it, when, what was delivered, and when it expired
**So that** I can prove during an audit that we honoured every Art. 15 request within SLA without leaking data.

**Depends on:** Story A

#### Acceptance criteria

- **Given** any export request (queued, in-progress, completed, failed, or expired), **When** the operator queries `GET /internal/exports?user_id=<id>` with an operator API key, **Then** they receive an ordered list of `export_request_log` rows with `request_id`, `user_id`, `requested_at`, `status`, `completed_at`, `download_count`, `expired_at`.
- **Given** a download link expires unused after 72 h, **When** the retention sweep runs (hourly), **Then** the ZIP file is deleted from the staging bucket, the `export_request_log` row is updated to `status="expired", expired_at=<now>`, and the deletion is recorded with a `deleted_by="retention_sweep"` audit field.
- **Given** an operator attempts to access export logs without an operator API key, **When** they call `GET /internal/exports`, **Then** the response is HTTP 401 and the attempt is logged to `audit_log` with the source IP and user agent.

## 4. Non-functional requirements

- **Performance:** Export job p95 duration < 6 h for users with < 100 k rows; < 24 h for users with up to 1 M rows. Request-enqueue endpoint p95 < 200 ms (the queue insert is the only synchronous DB write).
- **Security:** Download URLs are signed (HMAC-SHA256 over `request_id|user_id|expires_at` using a key from `EXPORT_SIGNING_KEY`), single-use (token marked consumed in `export_request_log.download_count` on first 200 response), and expire in 72 h. Operator API key required for `GET /internal/exports`. Staging bucket is private; signed URLs are the only access path.
- **Observability:** Every state transition on an export request emits a structured log line with `request_id`, `user_id` (hashed in logs), `from_status`, `to_status`, and duration. The `notification-service` `notification_log` row records `kind="user_data_export_ready"`. Metrics: `export_requests_total{status}`, `export_job_duration_seconds`, `export_link_downloads_total`, `export_link_expirations_total`.
- **Reliability:** Export worker retries transient failures up to 3 times with exponential backoff (1 min, 5 min, 25 min). Permanent failures (corrupt source data, missing user) move to `status="failed"` and notify the on-call operator via `notification-service` `kind="export_failed"`. No silent drops.
- **Cost:** ZIP archives stored in object storage at S3 Standard-IA pricing tier (~$0.0125/GB/month); 72 h max retention → average storage ~ $0.001 per export. Worker uses the existing user-service container at CPU-only sizing. Net cost target: < $0.05 per export at expected volume of ~200/quarter.
- **Privacy/Compliance:** Implements GDPR Art. 15 (right of access) and CCPA §1798.110. Internal SLA: 7 days median, 30 days absolute ceiling. PII in transit is TLS-only. The download URL never appears in URLs we log (logged as `<redacted-signed-url>`). User email is the legal delivery channel and is verified against the user's current email at job start, not at request time, to avoid stale-email leaks.
- **Accessibility:** The download-link email follows the `notification-service` plain-text + HTML template that meets WCAG 2.1 AA contrast and is screen-reader-tested.

## 5. Out of scope

- **Account deletion** — covered by a separate forthcoming PRD; export and deletion are legally distinct and we do not couple them in v1.
- **Third-party processor data** — data held by Stripe, SendGrid, or our analytics processor is the controller's responsibility to surface via their respective DSAR flows; we link to those flows in the export email but do not ingest their data.
- **Bulk operator exports** — operators cannot export data for many users at once via this endpoint; they must use the data-warehouse export which already has separate controls.
- **Export format selection (CSV vs JSON vs Parquet)** — ZIP-of-JSON only for v1; we will revisit if user demand or regulatory guidance changes.

## 6. Open questions

- Should the 72 h download window be configurable per region (e.g. EU 30 days vs CA 72 h)? **Owner:** PM, decision needed before public rollout.
- Should we offer the user an in-product receipt page in addition to the email (some users mark our emails as spam and miss the link)? **Owner:** designer + PM, decision deferred to post-MVP.
- Does the audit trail need to be exported to our SIEM in real-time, or is daily batch sufficient? **Owner:** security lead, decision needed by GA.

## 7. Rollout plan

1. **Feature flag** `export_self_service` (default `off`) gates the `POST /api/users/me/export` route and the operator `GET /internal/exports` route.
2. **Dark launch (week 1):** flag on for internal `@example.com` accounts only; verify end-to-end flow on real data with synthetic personal data for a handful of staff users.
3. **5% ramp (week 2):** flag on for 5% of users by stable hash of `user_id`. Monitor `export_job_duration_seconds` p95, `export_requests_total{status="failed"}` rate, and on-call pages.
4. **50% ramp (week 3):** if week 2 metrics within target, expand to 50%.
5. **100% (week 4):** GA. Announce in product release notes; update privacy policy with the new self-service path.
6. **Rollback plan:** flag flip to `off` reverts to the legacy support-ticket flow within < 5 min; no schema rollback needed because `export_request_log` is additive.

## Three Amigos Findings (run: 2026-05-27)

_Generated by the `decompose-epic` skill. Resolve each finding by editing the PRD body inline, then delete that bullet from this section. Re-run the skill to refresh._

### Dev Perspective (@pm-dev-perspective)

#### Story A — Request export

- **Dependencies:** `apps/user-service/app/routers/export.py` (new), `apps/user-service/app/services/export_worker.py` (new), `apps/api-gateway/src/main/java/.../controller/ExportController.java` (proxy + per-user rate limit), `apps/notification-service/internal/handler/notify.go` (new `kind="user_data_export_ready"`), `contracts/schemas/user_export.json` (new schema).
- **Hidden complexity:** Per-user rate limiting at the gateway requires a shared rate-limit store (Redis) or a sticky-session guarantee; the current `api-gateway` has only per-API-key token-bucket middleware, not per-user. Picking Redis adds an infra dependency; sticky sessions constrain the deployment topology.
- **Effort:** M — 2–3 days assuming Redis is acceptable; L if we need to design a stateless per-user limiter from scratch.

#### Story B — Format of the export

- **Dependencies:** `apps/user-service/app/services/export_worker.py` (assembles the ZIP), object storage client (`apps/user-service/app/clients/storage.py`, new), `contracts/schemas/user_export.json` (manifest shape).
- **Hidden complexity:** Snapshot semantics across multiple tables in the user-service Postgres need a repeatable-read transaction or explicit snapshot timestamp; otherwise rows added mid-export produce an internally inconsistent ZIP. SHA-256 of every file requires streaming hashing or memory will spike on large exports.
- **Effort:** L — 4–6 days including snapshot-semantics design and the streaming-hash plumbing.

#### Story C — Operator audit trail

- **Dependencies:** `apps/user-service/app/routers/internal_exports.py` (new), `apps/user-service/app/db/migrations/<NNNN>_export_request_log.sql` (new table), `apps/user-service/app/jobs/retention_sweep.py` (new hourly job), `apps/api-gateway/src/main/java/.../filter/OperatorApiKeyFilter.java` (new auth path).
- **Hidden complexity:** The retention sweep needs to coordinate with in-flight downloads — if a download starts at T=71h59m and takes 90 s to stream, the sweep at T=72h00m must not yank the object out from under it. Recommend marking the request `status="expiring"` at issue time and a 5-min grace before deletion.
- **Effort:** M — 3 days for the table, sweep, operator endpoint, and auth filter.

### QA Perspective (@pm-qa-perspective)

#### Story A — Request export

- **[Concurrency]** User opens the export page in two tabs and clicks "Request export" within 200 ms in both tabs. Test sketch: Given a logged-in user, When two `POST /api/users/me/export` requests arrive within 200 ms, Then exactly one returns HTTP 202 and the other returns HTTP 429 (or both deduplicate to the same `request_id`).
- **[Auth expiry]** Session expires between the request and the email arriving (~4 h later). Test sketch: Given a user whose session expires 30 min after request, When the export completes and the download email is sent, Then the link still works (link auth is the signed token, NOT the session) but the audit log records the request's original session and the link click's anonymous-but-token-authorised access.
- **[i18n]** User's email address is an IDN domain (e.g. `用户@例え.jp`). Test sketch: Given a user with an IDN email, When the export completes, Then `notification-service` delivers to the punycode-encoded form and the audit log records both the original and punycode form.
- **[Error state]** `notification-service` returns HTTP 503 when the export worker tries to send the link. Test sketch: Given a completed export and a down notification-service, When the worker calls `/notify`, Then the export job is marked `status="completed_pending_notification"`, retried up to 3 times with backoff, and on permanent failure escalated to operator audit log (the user data is still ready — losing the email must not lose the export).

#### Story B — Format of the export

- **[Empty input]** User has zero rows in every table (brand-new account that requested export before any activity). Test sketch: Given a user with no sessions, notifications, or support tickets, When they download the ZIP, Then every category file is present and contains `[]`, and `manifest.json` row counts are all zero — not missing.
- **[Concurrency]** User requests an account-deletion 30 s after requesting an export, and deletion runs first. Test sketch: Given a user who has POSTed `/export` at T=0 and `/account/delete` at T=30s, When the export job starts at T=60s after deletion has dropped rows, Then the worker MUST either (a) detect the snapshot is unrecoverable and mark `status="failed_user_deleted"` with operator notification, or (b) honour the export-at-T=0 snapshot if the deletion was deferred. Silent partial export is not acceptable.
- **[i18n]** User's `full_name` contains multi-byte UTF-8 (e.g. emoji or CJK) and the export filename is constructed from it. Test sketch: Given `full_name="李 雷 😀"`, When the ZIP filename is constructed, Then it does NOT include `full_name` (filename uses `user-{id}` to avoid filesystem encoding issues across the user's OS).
- **[Error state]** Object storage returns 500 mid-upload. Test sketch: Given an export job that has streamed 50% of a 200 MB ZIP, When the storage client returns 500, Then the worker discards the partial upload, retries with backoff, and never delivers a half-written ZIP.

#### Story C — Operator audit trail

- **[Concurrency]** Retention sweep fires while a download is in flight. Test sketch: Given a download started at T=71h59m, When the retention sweep runs at T=72h00m, Then the in-flight stream completes successfully (sweep respects the "expiring" 5-min grace per the dev finding) AND the row is marked `expired` after the grace.
- **[Auth expiry]** Operator API key is rotated mid-query. Test sketch: Given an operator with a paginated query in progress, When their API key is revoked between page 1 and page 2, Then page 2 returns HTTP 401 cleanly (no half-paginated audit data leaks).
- **[Error state]** `audit_log` insert fails when an unauthorised access attempt arrives. Test sketch: Given a flooded `audit_log` table or a database connection exhaustion, When an unauthenticated `GET /internal/exports` arrives, Then the response is still HTTP 401 (we never grant access on failed audit insert) and the audit-write failure is itself logged to stderr for alerting.

### Structural Gaps (@pm-gap-detector)

No structural gaps detected against prds/_template.md or .claude/rules/pm.md.
