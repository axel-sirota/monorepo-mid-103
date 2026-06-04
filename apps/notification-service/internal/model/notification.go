package model

// Notification is the inbound payload for POST /notify.
// It mirrors contracts/schemas/notification.json exactly.
type Notification struct {
	ToEmail  string                 `json:"to_email" binding:"required,email,max=320"`
	Subject  string                 `json:"subject" binding:"required,min=1,max=200"`
	Body     string                 `json:"body" binding:"required,min=1,max=10000"`
	Kind     string                 `json:"kind" binding:"required,oneof=churn_risk_alert welcome weekly_digest"`
	UserID   *int64                 `json:"user_id,omitempty" binding:"omitempty,min=1"`
	Metadata map[string]any         `json:"metadata,omitempty"`
}
