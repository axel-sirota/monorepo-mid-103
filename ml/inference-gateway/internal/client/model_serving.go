package client

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/example/inference-gateway/internal/model"
)

// UpstreamError signals an error returned by the upstream model-serving call.
type UpstreamError struct {
	StatusCode int
	Body       []byte
	Err        error
}

func (e *UpstreamError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("upstream error: %v", e.Err)
	}
	return fmt.Sprintf("upstream returned status %d", e.StatusCode)
}

// ModelServingClient is the interface used by the predict handler. Tests can substitute
// a fake implementation.
type ModelServingClient interface {
	Predict(ctx context.Context, req *model.PredictionRequest) (*model.PredictionResponse, error)
}

// HTTPClient is the production implementation of ModelServingClient.
type HTTPClient struct {
	BaseURL string
	HTTP    *http.Client
}

// New returns an HTTPClient with a sensible default timeout.
func New(baseURL string) *HTTPClient {
	return &HTTPClient{
		BaseURL: baseURL,
		HTTP:    &http.Client{Timeout: 10 * time.Second},
	}
}

// Predict sends the prediction request to the upstream service and returns the parsed response.
func (c *HTTPClient) Predict(ctx context.Context, req *model.PredictionRequest) (*model.PredictionResponse, error) {
	payload, err := json.Marshal(req)
	if err != nil {
		return nil, &UpstreamError{Err: err}
	}

	url := c.BaseURL + "/predict"
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(payload))
	if err != nil {
		return nil, &UpstreamError{Err: err}
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTP.Do(httpReq)
	if err != nil {
		return nil, &UpstreamError{Err: err}
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, &UpstreamError{StatusCode: resp.StatusCode, Err: err}
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, &UpstreamError{StatusCode: resp.StatusCode, Body: body}
	}

	var out model.PredictionResponse
	if err := json.Unmarshal(body, &out); err != nil {
		return nil, &UpstreamError{StatusCode: resp.StatusCode, Body: body, Err: err}
	}
	return &out, nil
}
