// Package validators provides shared validation utilities extracted from:
//   - apps/notification-service/internal/service/email_utils.go
//   - apps/user-service/app/services/user_service.py (Python equivalent)
//
// Lab 3 extraction target. Import this in notification-service to replace the local copy.
package validators

import (
	"regexp"
	"time"
)

var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`)

// ValidateEmail returns true if the email address matches RFC 5322 simplified pattern.
func ValidateEmail(email string) bool {
	return emailRegex.MatchString(email)
}

// FormatDate formats a time.Time to ISO 8601 UTC string.
func FormatDate(t time.Time) string {
	return t.UTC().Format(time.RFC3339)
}
