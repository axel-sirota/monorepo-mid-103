package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/example/notification-service/internal/model"
	"github.com/example/notification-service/internal/service"
)

// NotifyHandler binds the notifier service.
type NotifyHandler struct {
	notifier *service.Notifier
}

// NewNotifyHandler constructs the handler.
func NewNotifyHandler(notifier *service.Notifier) *NotifyHandler {
	return &NotifyHandler{notifier: notifier}
}

// Handle is the POST /notify endpoint.
func (h *NotifyHandler) Handle(c *gin.Context) {
	var msg model.Notification
	if err := c.ShouldBindJSON(&msg); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	res := h.notifier.Send(c.Request.Context(), msg)

	// Insert failures are a server problem regardless of SMTP outcome.
	if res.InsertEr != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to persist notification log: " + res.InsertEr.Error()})
		return
	}

	if !res.Sent {
		c.JSON(http.StatusBadGateway, gin.H{
			"id":    res.LogID,
			"error": "smtp send failed: " + res.SendErr.Error(),
		})
		return
	}

	c.JSON(http.StatusAccepted, gin.H{"id": res.LogID})
}
