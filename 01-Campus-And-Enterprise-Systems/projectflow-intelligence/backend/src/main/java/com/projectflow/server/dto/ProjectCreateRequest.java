package com.projectflow.server.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;
import java.util.UUID;

public class ProjectCreateRequest {

    @NotNull(message = "Workspace ID is required")
    private UUID workspaceId;

    private UUID workflowId;

    @NotBlank(message = "Project name is required")
    private String name;

    private String description;

    @NotNull(message = "Start date is required")
    private LocalDate startDate;

    @NotNull(message = "Target date is required")
    private LocalDate targetDate;

    public ProjectCreateRequest() {
    }

    public ProjectCreateRequest(UUID workspaceId, UUID workflowId, String name, String description, LocalDate startDate, LocalDate targetDate) {
        this.workspaceId = workspaceId;
        this.workflowId = workflowId;
        this.name = name;
        this.description = description;
        this.startDate = startDate;
        this.targetDate = targetDate;
    }

    public UUID getWorkspaceId() {
        return workspaceId;
    }

    public void setWorkspaceId(UUID workspaceId) {
        this.workspaceId = workspaceId;
    }

    public UUID getWorkflowId() {
        return workflowId;
    }

    public void setWorkflowId(UUID workflowId) {
        this.workflowId = workflowId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public void setStartDate(LocalDate startDate) {
        this.startDate = startDate;
    }

    public LocalDate getTargetDate() {
        return targetDate;
    }

    public void setTargetDate(LocalDate targetDate) {
        this.targetDate = targetDate;
    }
}
