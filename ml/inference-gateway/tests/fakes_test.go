package tests

import (
	"context"

	"github.com/example/inference-gateway/internal/client"
	"github.com/example/inference-gateway/internal/model"
)

// fakeUpstream is a shared test double for client.ModelServingClient.
type fakeUpstream struct {
	Response *model.PredictionResponse
	Err      error
	Calls    int
	LastReq  *model.PredictionRequest
}

func (f *fakeUpstream) Predict(_ context.Context, req *model.PredictionRequest) (*model.PredictionResponse, error) {
	f.Calls++
	f.LastReq = req
	if f.Err != nil {
		return nil, f.Err
	}
	if f.Response != nil {
		return f.Response, nil
	}
	return &model.PredictionResponse{
		UserID:           req.UserID,
		ChurnProbability: 0.5,
		RiskBand:         "medium",
		ModelVersion:     "v1",
	}, nil
}

// ensure compile-time interface conformance
var _ client.ModelServingClient = (*fakeUpstream)(nil)
