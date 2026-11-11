package com.projectflow.core.model;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class Workflow {
    private UUID id;
    private UUID workspaceId;
    private String name;
    private String description;
    private boolean isDefault;
    private List<WorkflowStatus> statuses = new ArrayList<>();
    private List<WorkflowTransition> transitions = new ArrayList<>();
    private Instant createdAt;
    private Instant updatedAt;

    public Workflow() {
    }

    public Workflow(UUID id, UUID workspaceId, String name, boolean isDefault) {
        this.id = id;
        this.workspaceId = workspaceId;
        this.name = name;
        this.isDefault = isDefault;
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
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

    public List<WorkflowStatus> getStatuses() {
        return statuses;
    }

    public void setStatuses(List<WorkflowStatus> statuses) {
        this.statuses = statuses;
    }

    public List<WorkflowTransition> getTransitions() {
        return transitions;
    }

    public void setTransitions(List<WorkflowTransition> transitions) {
        this.transitions = transitions;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
