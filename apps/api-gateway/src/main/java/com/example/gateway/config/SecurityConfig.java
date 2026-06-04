package com.example.gateway.config;

import org.springframework.context.annotation.Configuration;

/**
 * Security wiring marker. The {@link ApiKeyAuthFilter} is auto-registered by Spring Boot
 * as a {@code @Component} servlet filter. The filter itself decides which paths to gate
 * via {@code shouldNotFilter}: only requests under {@code /api/**} require X-API-Key.
 */
@Configuration
public class SecurityConfig {
}
