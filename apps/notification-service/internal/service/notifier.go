package service

import (
	"context"

	"github.com/example/notification-service/internal/model"
	"github.com/example/notification-service/internal/repository"
)

// Notifier orchestrates send + log. Returns the inserted log row id.
type Notifier struct {
	sender    Sender
	repo      *repository.NotificationLogRepository
	fromEmail string
}

// NewNotifier wires dependencies.
func NewNotifier(sender Sender, repo *repository.NotificationLogRepository, fromEmail string) *Notifier {
	return &Notifier{sender: sender, repo: repo, fromEmail: fromEmail}
}

// SendResult is what the handler needs back: the log row id, whether SMTP succeeded, and any error.
type SendResult struct {
	LogID    int64
	Sent     bool
	SendErr  error
	InsertEr error
}

// Send attempts to deliver the notification, then logs the attempt regardless of outcome.
func (n *Notifier) Send(ctx context.Context, msg model.Notification) SendResult {
	sendErr := n.sender.Send(n.fromEmail, msg.ToEmail, msg.Subject, msg.Body)
	status := "sent"
	if sendErr != nil {
		status = "failed"
	}

	id, insErr := n.repo.Insert(ctx, msg, status, sendErr)
	return SendResult{
		LogID:    id,
		Sent:     sendErr == nil,
		SendErr:  sendErr,
		InsertEr: insErr,
	}
}
