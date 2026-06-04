package tests

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"

	"github.com/example/inference-gateway/internal/router"
)

func TestRateLimit_BurstOverflow_Returns429(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// 60/min -> 1 token/sec, burst = 10. Fire 12 in rapid succession; expect at least one 429.
	r := router.SetupRouter(router.Deps{
		APIKey:             "k",
		RateLimitPerMinute: 60,
		Upstream:           &fakeUpstream{},
	})

	body := validRequestBody(t)

	var status429 int
	var status200 int
	for i := 0; i < 12; i++ {
		req := httptest.NewRequest(http.MethodPost, "/predict", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("X-API-Key", "k")
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		switch w.Code {
		case http.StatusTooManyRequests:
			status429++
		case http.StatusOK:
			status200++
		}
	}

	assert.GreaterOrEqual(t, status429, 1, "expected at least one 429 after burst")
	assert.GreaterOrEqual(t, status200, 1, "expected at least one 200 within burst capacity")
}

func TestRateLimit_429Body(t *testing.T) {
	gin.SetMode(gin.TestMode)

	r := router.SetupRouter(router.Deps{
		APIKey:             "k",
		RateLimitPerMinute: 60,
		Upstream:           &fakeUpstream{},
	})
	body := validRequestBody(t)

	var lastBody string
	for i := 0; i < 30; i++ {
		req := httptest.NewRequest(http.MethodPost, "/predict", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("X-API-Key", "k")
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		if w.Code == http.StatusTooManyRequests {
			lastBody = w.Body.String()
			break
		}
	}

	assert.JSONEq(t, `{"error":"rate_limit_exceeded"}`, lastBody)
}
