package com.example.gateway.client;

import com.example.gateway.model.ChurnRiskDto;
import com.example.gateway.model.UserCreateRequest;
import com.example.gateway.model.UserDto;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class UserServiceClient {

    private final RestClient restClient;

    public UserServiceClient(@Qualifier("userServiceRestClient") RestClient restClient) {
        this.restClient = restClient;
    }

    public UserDto getUser(Long id) {
        return restClient.get()
                .uri("/users/{id}", id)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(UserDto.class);
    }

    public UserDto createUser(UserCreateRequest request) {
        return restClient.post()
                .uri("/users")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(UserDto.class);
    }

    public ChurnRiskDto getChurnRisk(Long id) {
        return restClient.get()
                .uri("/users/{id}/churn-risk", id)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(ChurnRiskDto.class);
    }
}
