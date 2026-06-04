package router

import (
	"github.com/gin-gonic/gin"

	"github.com/example/notification-service/internal/handler"
	"github.com/example/notification-service/internal/middleware"
	"github.com/example/notification-service/internal/service"
)

// Deps holds optional dependencies; nil notifier means /notify is not mounted (used by health-only tests).
type Deps struct {
	Notifier *service.Notifier
}

// SetupRouter builds the gin engine. If deps.Notifier is nil, /notify is skipped.
func SetupRouter(deps Deps) *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery())
	r.Use(middleware.RequestID())
	r.Use(middleware.Logger())

	r.GET("/health", handler.Health)

	if deps.Notifier != nil {
		nh := handler.NewNotifyHandler(deps.Notifier)
		r.POST("/notify", nh.Handle)
	}

	return r
}
