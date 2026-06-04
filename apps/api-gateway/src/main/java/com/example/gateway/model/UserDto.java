package com.example.gateway.model;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;

public record UserDto(
        Long id,
        String email,
        @JsonProperty("full_name") String fullName,
        @JsonProperty("created_at") Instant createdAt,
        @JsonProperty("engagement_score") Double engagementScore,
        @JsonProperty("days_since_login") Integer daysSinceLogin,
        @JsonProperty("sessions_last_30d") Integer sessionsLast30d,
        @JsonProperty("support_tickets_last_90d") Integer supportTicketsLast90d
) {}
