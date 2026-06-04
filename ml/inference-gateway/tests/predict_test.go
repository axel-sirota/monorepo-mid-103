package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/example/inference-gateway/internal/client"
	"github.com/example/inference-gateway/internal/model"
	"github.com/example/inference-gateway/internal/router"
)

func TestPredict_PassesUpstreamResponseThrough(t *testing.T) {
	gin.SetMode(gin.TestMode)

	mockResp := &model.PredictionResponse{
		UserID:           42,
		ChurnProbability: 0.81,
		RiskBand:         "high",
		ModelVersion:     "v1",
	}
	up := &fakeUpstream{Response: mockResp}

	r := router.SetupRouter(router.Deps{
		APIKey:             "k",
		RateLimitPerMinute: 600,
		Upstream:           up,
	})

	body, _ := json.Marshal(model.PredictionRequest{
		UserID:                42,
		EngagementScore:       0.1,
		DaysSinceLogin:        45,
		SessionsLast30d:       1,
		SupportTicketsLast90d: 7,
	})
	req := httptest.NewRequest(http.MethodPost, "/predict", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", "k")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	require.Equal(t, http.StatusOK, w.Code)

	var got model.PredictionResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &got))
	assert.Equal(t, *mockResp, got)
	assert.Equal(t, 1, up.Calls)
	require.NotNil(t, up.LastReq)
	assert.Equal(t, 42, up.LastReq.UserID)
}

func TestPredict_UpstreamError_Returns502(t *testing.T) {
	gin.SetMode(gin.TestMode)

	up := &fakeUpstream{Err: &client.UpstreamError{StatusCode: 500, Body: []byte("boom")}}

	r := router.SetupRouter(router.Deps{
		APIKey:             "k",
		RateLimitPerMinute: 600,
		Upstream:           up,
	})

	body := validRequestBody(t)
	req := httptest.NewRequest(http.MethodPost, "/predict", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", "k")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	require.Equal(t, http.StatusBadGateway, w.Code)

	var payload map[string]interface{}
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &payload))
	assert.Equal(t, "upstream_error", payload["error"])
}

func TestPredict_InvalidRequest_Returns400(t *testing.T) {
	gin.SetMode(gin.TestMode)

	r := router.SetupRouter(router.Deps{
		APIKey:             "k",
		RateLimitPerMinute: 600,
		Upstream:           &fakeUpstream{},
	})

	req := httptest.NewRequest(http.MethodPost, "/predict", bytes.NewReader([]byte(`{"user_id":0}`)))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", "k")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}
