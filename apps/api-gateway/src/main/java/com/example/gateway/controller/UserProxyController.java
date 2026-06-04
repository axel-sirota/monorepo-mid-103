package com.example.gateway.controller;

import com.example.gateway.client.UserServiceClient;
import com.example.gateway.model.ChurnRiskDto;
import com.example.gateway.model.UserCreateRequest;
import com.example.gateway.model.UserDto;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/users")
public class UserProxyController {

    private final UserServiceClient client;

    public UserProxyController(UserServiceClient client) {
        this.client = client;
    }

    @GetMapping("/{id}")
    public UserDto getUser(@PathVariable("id") Long id) {
        return client.getUser(id);
    }

    @PostMapping
    public ResponseEntity<UserDto> createUser(@Valid @RequestBody UserCreateRequest request) {
        UserDto created = client.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}/churn-risk")
    public ChurnRiskDto churnRisk(@PathVariable("id") Long id) {
        return client.getChurnRisk(id);
    }
}
