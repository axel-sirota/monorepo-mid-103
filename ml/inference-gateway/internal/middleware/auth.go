package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

const apiKeyHeader = "X-API-Key"

// APIKeyAuth verifies the X-API-Key header matches the configured key.
// It also stores the key on the context so downstream middleware (rate-limit) can use it.
func APIKeyAuth(expectedKey string) gin.HandlerFunc {
	return func(c *gin.Context) {
		got := c.GetHeader(apiKeyHeader)
		if got == "" || got != expectedKey {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized"})
			return
		}
		c.Set("api_key", got)
		c.Next()
	}
}
