package model

import (
	"database/sql"
	"time"
)

// NotificationLog is one row in the notification_log table.
type NotificationLog struct {
	ID        int64          `db:"id"`
	ToEmail   string         `db:"to_email"`
	Subject   string         `db:"subject"`
	Body      string         `db:"body"`
	Kind      string         `db:"kind"`
	UserID    sql.NullInt64  `db:"user_id"`
	Metadata  []byte         `db:"metadata"` // JSONB as raw bytes
	Status    string         `db:"status"`   // "sent" | "failed"
	Error     sql.NullString `db:"error"`
	CreatedAt time.Time      `db:"created_at"`
}
