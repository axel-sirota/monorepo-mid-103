package com.example.gateway.model;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;

// BUG: class-bug-5 (contract-cop): field uses snake_case Java identifier instead of camelCase
// + @JsonProperty. Schema defines "created_at"; Java convention requires camelCase field names.
public record UserDto(
        Long id,
        String email,
        @JsonProperty("full_name") String fullName,
        Instant created_at,
        @JsonProperty("engagement_score") Double engagementScore,
        @JsonProperty("days_since_login") Integer daysSinceLogin,
        @JsonProperty("sessions_last_30d") Integer sessionsLast30d,
        @JsonProperty("support_tickets_last_90d") Integer supportTicketsLast90d
) {}
