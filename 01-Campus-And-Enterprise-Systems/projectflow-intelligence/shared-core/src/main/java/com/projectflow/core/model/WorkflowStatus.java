package com.projectflow.core.model;

import java.util.UUID;

public class WorkflowStatus {
    private UUID id;
    private UUID workflowId;
    private String name;
    private String color;
    private StatusCategory category;
    private int position;

    public WorkflowStatus() {
    }

    public WorkflowStatus(UUID id, UUID workflowId, String name, String color, StatusCategory category, int position) {
        this.id = id;
        this.workflowId = workflowId;
        this.name = name;
        this.color = color;
        this.category = category;
        this.position = position;
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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public StatusCategory getCategory() {
        return category;
    }

    public void setCategory(StatusCategory category) {
        this.category = category;
    }

    public int getPosition() {
        return position;
    }

    public void setPosition(int position) {
        this.position = position;
    }

    public boolean isTerminal() {
        return category != null && category.isTerminal();
    }
}
