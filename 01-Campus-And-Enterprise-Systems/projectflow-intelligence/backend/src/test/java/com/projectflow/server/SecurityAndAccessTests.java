package com.projectflow.server;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class SecurityAndAccessTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void unauthenticatedRequestShouldReturn401() throws Exception {
        mockMvc.perform(get("/api/v1/workspaces"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void healthEndpointShouldBePubliclyAccessible() throws Exception {
        mockMvc.perform(get("/actuator/health"))
                .andExpect(status().isOk());
    }

    @Test
    void devLoginShouldReturnValidToken() throws Exception {
        mockMvc.perform(post("/api/v1/auth/dev-login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"admin@projectflow.io\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accessToken").value("dev-admin-token"))
                .andExpect(jsonPath("$.user.globalRole").value("ADMINISTRATOR"));
    }

    @Test
    void adminEndpointWithDevAdminTokenShouldSucceed() throws Exception {
        mockMvc.perform(get("/api/v1/admin/overview")
                        .header("Authorization", "Bearer dev-admin-token"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.systemStatus").value("OPERATIONAL"));
    }

    @Test
    void adminEndpointWithMemberTokenShouldReturn403() throws Exception {
        mockMvc.perform(get("/api/v1/admin/overview")
                        .header("Authorization", "Bearer dev-member-token"))
                .andExpect(status().isForbidden());
    }
}
