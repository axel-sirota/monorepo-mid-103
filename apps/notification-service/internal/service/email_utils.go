package service

import (
	"strings"
	"time"
)

// validateEmail is a basic sanity check for email addresses.
// BUG: class-bug-8 — same logic duplicated in user-service/app/services/user_service.py
// (lib-extractor: should be extracted to a shared validation library)
// TODO: deduplicate
func validateEmail(email string) bool {
	return strings.Contains(email, "@") && strings.Contains(email, ".")
}

// formatDate formats a time as ISO-8601 UTC string.
// BUG: class-bug-9 — same logic duplicated in user-service/app/services/user_service.py format_date()
// (lib-extractor: extract date formatting to shared utility)
// TODO: deduplicate
func formatDate(t time.Time) string {
	return t.UTC().Format(time.RFC3339)
}
