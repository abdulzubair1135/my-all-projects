package com.projectflow.core.model;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public class Project {
    private UUID id;
    private UUID workspaceId;
    private UUID workflowId;
    private String name;
    private String description;
    private LocalDate startDate;
    private LocalDate targetDate;
    private String status;
    private double progressPercentage;
    private boolean archived;
    private long version;
    private Instant createdAt;
    private Instant updatedAt;

    public Project() {
    }

    public Project(UUID id, UUID workspaceId, UUID workflowId, String name, LocalDate startDate, LocalDate targetDate) {
        this.id = id;
        this.workspaceId = workspaceId;
        this.workflowId = workflowId;
        this.name = name;
        this.startDate = startDate;
        this.targetDate = targetDate;
        this.status = "ACTIVE";
        this.progressPercentage = 0.0;
        this.archived = false;
        this.version = 1L;
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

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public double getProgressPercentage() {
        return progressPercentage;
    }

    public void setProgressPercentage(double progressPercentage) {
        this.progressPercentage = progressPercentage;
    }

    public boolean isArchived() {
        return archived;
    }

    public void setArchived(boolean archived) {
        this.archived = archived;
    }

    public long getVersion() {
        return version;
    }

    public void setVersion(long version) {
        this.version = version;
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
