package com.example.gateway.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class RestClientConfig {

    @Bean
    public RestClient.Builder userServiceRestClientBuilder() {
        return RestClient.builder();
    }

    @Bean(name = "userServiceRestClient")
    public RestClient userServiceRestClient(@Qualifier("userServiceRestClientBuilder") RestClient.Builder builder,
                                            @Value("${gateway.user-service.url}") String baseUrl) {
        return builder.baseUrl(baseUrl).build();
    }

    @Bean(name = "notificationServiceRestClient")
    public RestClient notificationServiceRestClient(@Value("${gateway.notification-service.url}") String baseUrl) {
        return RestClient.builder().baseUrl(baseUrl).build();
    }
}
