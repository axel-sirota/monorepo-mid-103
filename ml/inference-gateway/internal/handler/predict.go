package handler

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/example/inference-gateway/internal/client"
	"github.com/example/inference-gateway/internal/model"
)

// Predict returns a gin handler that validates the incoming request and proxies it to the
// upstream model-serving client.
func Predict(upstream client.ModelServingClient) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req model.PredictionRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid_request", "detail": err.Error()})
			return
		}

		resp, err := upstream.Predict(c.Request.Context(), &req)
		if err != nil {
			var ue *client.UpstreamError
			if errors.As(err, &ue) {
				c.JSON(http.StatusBadGateway, gin.H{
					"error":           "upstream_error",
					"upstream_status": ue.StatusCode,
				})
				return
			}
			c.JSON(http.StatusBadGateway, gin.H{"error": "upstream_error"})
			return
		}

		c.JSON(http.StatusOK, resp)
	}
}
