package com.example.gateway.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Custom /health endpoint to back the docker-compose healthcheck.
 * The actuator is also enabled, but the contract requires {@code {"status":"ok"}}
 * at exactly {@code /health} — which differs from actuator's default JSON shape.
 */
@RestController
public class HealthController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "ok");
    }
}
