// Template: copy into apps/api-gateway/src/test/java/com/example/gateway/controller/{{NAME}}ControllerTest.java
// Replace {{NAME}}, {{METHOD}}, {{ENDPOINT}}, {{EXPECTED_STATUS}}.
// Assertion bodies should reflect the shape in contracts/schemas/*.json — not just "endpoint exists".

package com.example.gateway.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest({{NAME}}Controller.class)
class {{NAME}}ControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void {{METHOD}}_{{NAME}}_returns_{{EXPECTED_STATUS}}() throws Exception {
        mockMvc.perform({{METHOD}}("{{ENDPOINT}}")
                .header("X-API-Key", "test-key")
                .contentType("application/json")
                .content("{ /* request body matching contracts/schemas/*.json */ }"))
            .andExpect(status().is{{EXPECTED_STATUS}}())
            .andExpect(jsonPath("$.field_from_contract").exists());
    }
}
