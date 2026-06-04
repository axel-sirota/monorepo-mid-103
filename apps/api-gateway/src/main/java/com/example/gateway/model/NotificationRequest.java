package com.example.gateway.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.util.Map;

public record NotificationRequest(
        @JsonProperty("to_email") @NotBlank @Email @Size(max = 320) String toEmail,
        @NotBlank @Size(min = 1, max = 200) String subject,
        @NotBlank @Size(min = 1, max = 10000) String body,
        @NotBlank @Pattern(regexp = "churn_risk_alert|welcome|weekly_digest") String kind,
        @JsonProperty("user_id") Long userId,
        Map<String, Object> metadata
) {}
