package middleware

import (
	"log"
	"time"

	"github.com/gin-gonic/gin"
)

// StructuredLogger logs one line per request with method, path, status, latency, and request id.
func StructuredLogger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		latency := time.Since(start)
		reqID, _ := c.Get("request_id")
		log.Printf("level=info method=%s path=%s status=%d latency_ms=%d request_id=%v",
			c.Request.Method, c.Request.URL.Path, c.Writer.Status(), latency.Milliseconds(), reqID)
	}
}
