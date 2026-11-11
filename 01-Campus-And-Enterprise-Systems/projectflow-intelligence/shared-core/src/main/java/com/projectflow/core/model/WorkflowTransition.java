package com.projectflow.core.model;

import java.util.UUID;

public class WorkflowTransition {
    private UUID id;
    private UUID workflowId;
    private UUID fromStatusId;
    private UUID toStatusId;
    private String name;

    public WorkflowTransition() {
    }

    public WorkflowTransition(UUID id, UUID workflowId, UUID fromStatusId, UUID toStatusId, String name) {
        this.id = id;
        this.workflowId = workflowId;
        this.fromStatusId = fromStatusId;
        this.toStatusId = toStatusId;
        this.name = name;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getWorkflowId() {
        return workflowId;
    }

    public void setWorkflowId(UUID workflowId) {
        this.workflowId = workflowId;
    }

    public UUID getFromStatusId() {
        return fromStatusId;
    }

    public void setFromStatusId(UUID fromStatusId) {
        this.fromStatusId = fromStatusId;
    }

    public UUID getToStatusId() {
        return toStatusId;
    }

    public void setToStatusId(UUID toStatusId) {
        this.toStatusId = toStatusId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
