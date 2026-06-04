package com.example.gateway.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public record ChurnRiskDto(
        @JsonProperty("user_id") Long userId,
        @JsonProperty("churn_probability") Double churnProbability,
        @JsonProperty("risk_band") String riskBand,
        @JsonProperty("model_version") String modelVersion
) {}
