package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// Health returns 200 + {"status":"ok"} unconditionally.
func Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
