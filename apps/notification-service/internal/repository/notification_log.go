package repository

import (
	"context"
	"database/sql"
	"encoding/json"

	"github.com/jmoiron/sqlx"

	"github.com/example/notification-service/internal/model"
)

// NotificationLogRepository persists notification send attempts.
type NotificationLogRepository struct {
	db *sqlx.DB
}

// NewNotificationLogRepository constructs the repo.
func NewNotificationLogRepository(db *sqlx.DB) *NotificationLogRepository {
	return &NotificationLogRepository{db: db}
}

// Insert writes a row and returns the generated id.
func (r *NotificationLogRepository) Insert(ctx context.Context, n model.Notification, status string, sendErr error) (int64, error) {
	var metaBytes []byte
	if n.Metadata != nil {
		b, err := json.Marshal(n.Metadata)
		if err != nil {
			return 0, err
		}
		metaBytes = b
	}

	var userID sql.NullInt64
	if n.UserID != nil {
		userID = sql.NullInt64{Int64: *n.UserID, Valid: true}
	}

	var errStr sql.NullString
	if sendErr != nil {
		errStr = sql.NullString{String: sendErr.Error(), Valid: true}
	}

	const q = `
		INSERT INTO notification_log (to_email, subject, body, kind, user_id, metadata, status, error)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		RETURNING id`

	var id int64
	row := r.db.QueryRowxContext(ctx, q,
		n.ToEmail, n.Subject, n.Body, n.Kind, userID, metaBytes, status, errStr,
	)
	if err := row.Scan(&id); err != nil {
		return 0, err
	}
	return id, nil
}
