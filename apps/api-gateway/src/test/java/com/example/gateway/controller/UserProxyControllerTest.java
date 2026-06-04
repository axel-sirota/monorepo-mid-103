package com.example.gateway.controller;

import com.example.gateway.config.ApiKeyAuthFilter;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.client.RestClient;
import org.springframework.web.context.WebApplicationContext;

import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(classes = {com.example.gateway.GatewayApplication.class, UserProxyControllerTest.TestConfig.class})
@TestPropertySource(properties = {
        "API_KEY=test-key-correct",
        "USER_SERVICE_URL=http://user-service-mock:8001",
        "NOTIFICATION_SERVICE_URL=http://notification-service-mock:8002",
        "spring.main.allow-bean-definition-overriding=true"
})
class UserProxyControllerTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private ApiKeyAuthFilter apiKeyAuthFilter;

    @Autowired
    private MockRestServiceServer mockServer;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        mockServer.reset();
        // MockMvc's webAppContextSetup does not auto-register servlet filters; add the
        // ApiKeyAuthFilter explicitly so the 401 gate runs in the test pipeline.
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext)
                .addFilter(apiKeyAuthFilter, "/api/*")
                .build();
    }

    @Test
    void getUser_withoutApiKey_returns401() throws Exception {
        mockMvc.perform(get("/api/users/1"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void getUser_withWrongApiKey_returns401() throws Exception {
        mockMvc.perform(get("/api/users/1").header("X-API-Key", "wrong-key"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void getUser_withCorrectApiKey_returnsUpstreamBody() throws Exception {
        String upstreamJson = """
                {
                  "id": 1,
                  "email": "ada@example.com",
                  "full_name": "Ada Lovelace",
                  "created_at": "2026-01-15T09:30:00Z",
                  "engagement_score": 0.82,
                  "days_since_login": 2,
                  "sessions_last_30d": 17,
                  "support_tickets_last_90d": 0
                }
                """;

        mockServer.expect(requestTo("http://user-service-mock:8001/users/1"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(upstreamJson, MediaType.APPLICATION_JSON));

        mockMvc.perform(get("/api/users/1").header("X-API-Key", "test-key-correct"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.email").value("ada@example.com"))
                .andExpect(jsonPath("$.full_name").value("Ada Lovelace"))
                .andExpect(jsonPath("$.engagement_score").value(0.82));

        mockServer.verify();
    }

    /**
     * Replaces the production {@code userServiceRestClient} bean with one whose HTTP
     * traffic is intercepted by {@link MockRestServiceServer}. Order matters:
     * MockRestServiceServer must be bound to the builder BEFORE the RestClient is built,
     * otherwise the binding has no effect on the already-constructed client.
     */
    @TestConfiguration
    static class TestConfig {

        @Bean
        public RestClient.Builder mockedRestClientBuilder() {
            return RestClient.builder();
        }

        @Bean
        public MockRestServiceServer mockRestServiceServer(RestClient.Builder mockedRestClientBuilder) {
            // Bind FIRST, so the builder is instrumented before any RestClient is built from it.
            return MockRestServiceServer.bindTo(mockedRestClientBuilder).build();
        }

        @Bean(name = "userServiceRestClient")
        @Primary
        public RestClient userServiceRestClient(RestClient.Builder mockedRestClientBuilder,
                                                MockRestServiceServer mockRestServiceServer) {
            // The MockRestServiceServer parameter is unused at runtime but forces Spring to
            // build the mock server bean BEFORE constructing this RestClient, so the
            // builder's request factory is the mock factory by the time .build() runs.
            return mockedRestClientBuilder.baseUrl("http://user-service-mock:8001").build();
        }
    }
}
