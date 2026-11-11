package com.projectflow.server;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.time.LocalDate;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class CoreProjectManagementTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void shouldExecuteFullProjectManagementLifecycle() throws Exception {
        String token = "Bearer dev-admin-token";

        // 1. Create Workspace
        String wsPayload = "{\"name\":\"Engineering Workspace\",\"description\":\"Main Engineering Team\"}";
        MvcResult wsResult = mockMvc.perform(post("/api/v1/workspaces")
                        .header("Authorization", token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(wsPayload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Engineering Workspace"))
                .andReturn();

        JsonNode wsJson = objectMapper.readTree(wsResult.getResponse().getContentAsString());
        String workspaceId = wsJson.get("id").asText();

        // 2. Fetch Workflows for Workspace (auto-created default workflow)
        MvcResult wfResult = mockMvc.perform(get("/api/v1/workflows?workspaceId=" + workspaceId)
                        .header("Authorization", token))
                .andExpect(status().isOk())
                .andReturn();

        JsonNode wfArray = objectMapper.readTree(wfResult.getResponse().getContentAsString());
        assertThat(wfArray.size()).isGreaterThanOrEqualTo(1);
        String workflowId = wfArray.get(0).get("id").asText();
        String todoStatusId = wfArray.get(0).get("statuses").get(1).get("id").asText();
        String inProgressStatusId = wfArray.get(0).get("statuses").get(2).get("id").asText();

        // 3. Create Project
        LocalDate start = LocalDate.now();
        LocalDate target = start.plusDays(30);
        String projPayload = String.format(
                "{\"workspaceId\":\"%s\",\"workflowId\":\"%s\",\"name\":\"Core Engine V2\",\"startDate\":\"%s\",\"targetDate\":\"%s\"}",
                workspaceId, workflowId, start, target
        );

        MvcResult projResult = mockMvc.perform(post("/api/v1/projects")
                        .header("Authorization", token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(projPayload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Core Engine V2"))
                .andReturn();

        JsonNode projJson = objectMapper.readTree(projResult.getResponse().getContentAsString());
        String projectId = projJson.get("id").asText();

        // 4. Create Task
        String taskPayload = String.format(
                "{\"projectId\":\"%s\",\"title\":\"Architecture Design\",\"priority\":\"HIGH\",\"statusId\":\"%s\",\"dueDate\":\"%s\",\"estimatedHours\":16.0}",
                projectId, todoStatusId, start.plusDays(5)
        );

        MvcResult taskResult = mockMvc.perform(post("/api/v1/tasks")
                        .header("Authorization", token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(taskPayload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.title").value("Architecture Design"))
                .andReturn();

        JsonNode taskJson = objectMapper.readTree(taskResult.getResponse().getContentAsString());
        String taskId = taskJson.get("id").asText();

        // 5. Transition Task to In Progress
        String transitionPayload = String.format("{\"targetStatusId\":\"%s\"}", inProgressStatusId);
        mockMvc.perform(post("/api/v1/tasks/" + taskId + "/transitions")
                        .header("Authorization", token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(transitionPayload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.statusName").value("In Progress"));

        // 6. Recalculate Project Risks (empty or clean deterministic evaluation)
        mockMvc.perform(post("/api/v1/projects/" + projectId + "/risks/recalculate")
                        .header("Authorization", token))
                .andExpect(status().isOk());
    }
}
