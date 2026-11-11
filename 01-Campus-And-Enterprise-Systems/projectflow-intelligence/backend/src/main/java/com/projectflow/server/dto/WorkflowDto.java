package com.projectflow.server.dto;

import com.projectflow.core.model.StatusCategory;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class WorkflowDto {
    private UUID id;
    private UUID workspaceId;
    private String name;
    private String description;
    private boolean isDefault;
    private List<WorkflowStatusDto> statuses = new ArrayList<>();
    private List<WorkflowTransitionDto> transitions = new ArrayList<>();
    private Instant createdAt;

    public WorkflowDto() {
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getWorkspaceId() {
        return workspaceId;
    }

    public void setWorkspaceId(UUID workspaceId) {
        this.workspaceId = workspaceId;
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

    public boolean isDefault() {
        return isDefault;
    }

    public void setDefault(boolean aDefault) {
        isDefault = aDefault;
    }

    public List<WorkflowStatusDto> getStatuses() {
        return statuses;
    }

    public void setStatuses(List<WorkflowStatusDto> statuses) {
        this.statuses = statuses;
    }

    public List<WorkflowTransitionDto> getTransitions() {
        return transitions;
    }

    public void setTransitions(List<WorkflowTransitionDto> transitions) {
        this.transitions = transitions;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
