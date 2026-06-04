# PRD 0001 — Churn risk notification

**Status:** implemented
**Owner:** PM (seed PRD — written by the framework, not by a real PM)
**Last updated:** 2026-05-26
**Touches:** apps/api-gateway, apps/user-service, apps/notification-service, ml/model-serving, ml/inference-gateway, ml/training
**Contracts:** `contracts/schemas/user.json`, `contracts/schemas/notification.json`, `contracts/schemas/prediction.json`

## 1. Why

Active users churn silently. By the time billing notices, they're gone. We want to detect at-risk users *before* they cancel and reach out with a targeted re-engagement email. This PRD is the seed feature the monorepo currently implements.

## 2. Success metrics

- **Adoption (technical):** every active user has a churn score updated weekly. Baseline: 0 today.
- **Engagement:** opens of the churn-risk email ≥ 25% (P50 across cohorts).
- **Recovery:** at least 8% of high-risk users who receive the email return within 14 days.
- **System health:** end-to-end (score → email sent) p95 latency under 2 s.

## 3. User stories

### Story A — Predict churn probability for a user
**As a** product team
**I want** to compute a churn probability for any registered user given their engagement features
**So that** we can decide whether to intervene before they cancel.

**Depends on:** none

#### Acceptance criteria

- **Given** a user with `engagement_score=0.32, days_since_login=28, sessions_last_30d=2, support_tickets_last_90d=4`, **When** I call `POST /predict` on `inference-gateway` with a valid API key, **Then** I receive a `churn_probability` between 0 and 1 and a `risk_band` of `low | medium | high`.
- **Given** the same request without an API key, **When** I call `POST /predict`, **Then** the response is HTTP 401.
- **Given** 100 requests in 60 seconds with one API key, **When** the 101st arrives, **Then** the response is HTTP 429.
- **Given** the model artifact is missing on disk at boot, **When** `model-serving` starts, **Then** the `/health` endpoint returns 503 until the artifact appears.

### Story B — Email at-risk users
**As a** marketing operator
**I want** the system to send a re-engagement email to any user whose risk band is `high`
**So that** I don't have to babysit a dashboard.

**Depends on:** Story A

#### Acceptance criteria

- **Given** a user is scored `high`, **When** the api-gateway's churn-check job runs, **Then** `notification-service` receives one POST `/notify` with `kind = "churn_risk_alert"` and the user's email.
- **Given** the same user is scored `high` again within 7 days, **When** the job runs, **Then** no duplicate notification is sent (idempotency by `user_id + kind + 7-day window`).
- **Given** SMTP is down, **When** a send is attempted, **Then** the notification is logged with `status = "failed"` and a structured error is emitted; the request returns HTTP 502.

### Story C — Retrain the model on demand
**As a** data scientist
**I want** a one-shot training command that ingests the synthetic dataset, trains a logistic regression, logs to MLflow, and writes the model artifact to the shared volume
**So that** I can iterate on features without standing up training infra.

**Depends on:** none

#### Acceptance criteria

- **Given** a clean checkout, **When** I run `make train`, **Then** an MLflow run appears with `params`, `metrics`, and an `artifact_uri` pointing at the serialized model.
- **Given** training completes successfully, **When** I run `make predict`, **Then** I receive a probability for the sample payload using the just-trained model.

## 4. Non-functional requirements

- **Performance:** end-to-end churn score lookup p95 ≤ 800 ms; full notification dispatch p95 ≤ 2 s.
- **Security:** `inference-gateway` requires API key. `api-gateway` requires API key. Postgres is reachable only on the docker network. No PII in logs (emails redacted).
- **Observability:** every cross-service call carries an `X-Request-Id`. `notification-service` writes a `notification_log` row per send attempt.
- **Reliability:** transient failures retry once with backoff; permanent failures dead-letter to log.
- **Cost:** model-serving CPU-only (no GPU). One Postgres instance shared across services (separate databases).
- **Privacy/Compliance:** emails redacted from logs above DEBUG. `notification_log.body` retained 30 days, then truncated.

## 5. Out of scope

- Multi-channel notifications (SMS, in-app) — email only for v1.
- Adaptive re-targeting based on email engagement — fire once and observe.
- A/B test scaffolding for email content — copy is hardcoded.
- A dashboard for marketing ops — Mailhog UI is the dev surface; production observability is a separate PRD.

## 6. Open questions

- Whether the 7-day idempotency window should be configurable per cohort. **Owner:** PM.
- Whether `engagement_score` should be sourced from user-service directly or computed in `model-serving` from raw events. **Owner:** data-scientist.

## 7. Rollout plan

Seed feature — already live in the repo on day 1. No flag, no migration.
