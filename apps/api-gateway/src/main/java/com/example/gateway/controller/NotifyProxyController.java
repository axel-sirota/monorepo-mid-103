package com.example.gateway.controller;

import com.example.gateway.client.NotificationServiceClient;
import com.example.gateway.model.NotificationRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/notify")
public class NotifyProxyController {

    private final NotificationServiceClient client;

    public NotifyProxyController(NotificationServiceClient client) {
        this.client = client;
    }

    @PostMapping
    public ResponseEntity<String> notify(@Valid @RequestBody NotificationRequest request) {
        // We forward to notification-service. The contract for the gateway is 202 ACCEPTED
        // (the actual delivery is async at the notification-service / SMTP level).
        client.notify(request);
        return ResponseEntity.status(HttpStatus.ACCEPTED).build();
    }
}
