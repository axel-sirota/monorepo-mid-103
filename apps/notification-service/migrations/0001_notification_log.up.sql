CREATE TABLE notification_log (
    id         BIGSERIAL PRIMARY KEY,
    to_email   VARCHAR(320) NOT NULL,
    subject    VARCHAR(200) NOT NULL,
    body       TEXT NOT NULL,
    kind       VARCHAR(50) NOT NULL,
    user_id    BIGINT NULL,
    metadata   JSONB NULL,
    status     VARCHAR(20) NOT NULL,
    error      TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notification_log_kind_user ON notification_log (kind, user_id);
