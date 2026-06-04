package tests

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"

	"github.com/example/inference-gateway/internal/router"
)

func TestHealth_Returns200AndOK(t *testing.T) {
	gin.SetMode(gin.TestMode)

	r := router.SetupRouter(router.Deps{
		APIKey:             "test-key",
		RateLimitPerMinute: 60,
		Upstream:           &fakeUpstream{},
	})

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.JSONEq(t, `{"status":"ok"}`, w.Body.String())
}

func TestHealth_NoAuthRequired(t *testing.T) {
	gin.SetMode(gin.TestMode)

	r := router.SetupRouter(router.Deps{
		APIKey:             "test-key",
		RateLimitPerMinute: 60,
		Upstream:           &fakeUpstream{},
	})

	// No X-API-Key header — must still succeed.
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}
