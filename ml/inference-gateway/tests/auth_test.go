package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"

	"github.com/example/inference-gateway/internal/model"
	"github.com/example/inference-gateway/internal/router"
)

func validRequestBody(t *testing.T) []byte {
	t.Helper()
	body, err := json.Marshal(model.PredictionRequest{
		UserID:                1,
		EngagementScore:       0.42,
		DaysSinceLogin:        3,
		SessionsLast30d:       10,
		SupportTicketsLast90d: 0,
	})
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	return body
}

func newRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	return router.SetupRouter(router.Deps{
		APIKey:             "secret-key",
		RateLimitPerMinute: 60,
		Upstream:           &fakeUpstream{},
	})
}

func TestAuth_PredictWithoutKey_Returns401(t *testing.T) {
	r := newRouter()
	req := httptest.NewRequest(http.MethodPost, "/predict", bytes.NewReader(validRequestBody(t)))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestAuth_PredictWithWrongKey_Returns401(t *testing.T) {
	r := newRouter()
	req := httptest.NewRequest(http.MethodPost, "/predict", bytes.NewReader(validRequestBody(t)))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", "nope")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestAuth_PredictWithCorrectKey_Returns200(t *testing.T) {
	r := newRouter()
	req := httptest.NewRequest(http.MethodPost, "/predict", bytes.NewReader(validRequestBody(t)))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", "secret-key")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}
