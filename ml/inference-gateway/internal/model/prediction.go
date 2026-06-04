package model

// PredictionRequest mirrors contracts/schemas/prediction.json -> PredictionRequest.
type PredictionRequest struct {
	UserID                int     `json:"user_id" binding:"required,min=1"`
	EngagementScore       float64 `json:"engagement_score" binding:"required,min=0,max=1"`
	DaysSinceLogin        int     `json:"days_since_login" binding:"min=0"`
	SessionsLast30d       int     `json:"sessions_last_30d" binding:"min=0"`
	SupportTicketsLast90d int     `json:"support_tickets_last_90d" binding:"min=0"`
}

// PredictionResponse mirrors contracts/schemas/prediction.json -> PredictionResponse.
type PredictionResponse struct {
	UserID           int     `json:"user_id"`
	ChurnProbability float64 `json:"churn_probability"`
	RiskBand         string  `json:"risk_band,omitempty"`
	ModelVersion     string  `json:"model_version"`
}
