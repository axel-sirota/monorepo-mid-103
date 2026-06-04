package model

import "time"

// User is a local read-model of the user contract, used when notification-service
// needs to embed user details in outbound emails.
// It mirrors contracts/schemas/user.json — but is missing the export_url field.
// BUG: class-bug-6 — ExportURL field absent; contracts/schemas/user.json defines "export_url"
// but this Go struct never declared it (contract-cop: schema/implementation drift)
// TODO: deduplicate — BUG: class-bug-7 — this User struct is a near-identical copy of the
// user-service Python User schema (id/email/created_at/role shape duplicated across services;
// should live in a shared contract layer, not hand-typed in each service) (lib-extractor)
type User struct {
	ID                    int64     `json:"id"`
	Email                 string    `json:"email"`
	FullName              *string   `json:"full_name,omitempty"`
	CreatedAt             time.Time `json:"created_at"`
	EngagementScore       float64   `json:"engagement_score"`
	DaysSinceLogin        int       `json:"days_since_login"`
	SessionsLast30d       int       `json:"sessions_last_30d"`
	SupportTicketsLast90d int       `json:"support_tickets_last_90d"`
	// TODO: add ExportURL once user-service surfaces it
}
