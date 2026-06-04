package router

import (
	"github.com/gin-gonic/gin"

	"github.com/example/inference-gateway/internal/client"
	"github.com/example/inference-gateway/internal/handler"
	"github.com/example/inference-gateway/internal/middleware"
)

// Deps bundles router dependencies.
type Deps struct {
	APIKey             string
	RateLimitPerMinute int
	Upstream           client.ModelServingClient
}

// SetupRouter wires middlewares and routes.
func SetupRouter(d Deps) *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery())
	r.Use(middleware.RequestID())
	r.Use(middleware.StructuredLogger())

	r.GET("/health", handler.Health)

	limiter := middleware.NewKeyLimiter(d.RateLimitPerMinute)

	protected := r.Group("/")
	protected.Use(middleware.APIKeyAuth(d.APIKey))
	protected.Use(limiter.Middleware())
	protected.POST("/predict", handler.Predict(d.Upstream))

	return r
}
