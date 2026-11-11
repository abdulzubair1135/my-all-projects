package com.projectflow.server.dto;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class ScenarioDto {
    private UUID id;
    private UUID projectId;
    private String name;
    private String description;
    private UUID createdById;
    private boolean applied;
    private Instant appliedAt;
    private Long baseProjectVersion;
    private List<ScenarioCreateRequest.ScenarioChangeItem> changes = new ArrayList<>();
    private Instant createdAt;

    public ScenarioDto() {
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getProjectId() {
        return projectId;
    }

    public void setProjectId(UUID projectId) {
        this.projectId = projectId;
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

    public UUID getCreatedById() {
        return createdById;
    }

    public void setCreatedById(UUID createdById) {
        this.createdById = createdById;
    }

    public boolean isApplied() {
        return applied;
    }

    public void setApplied(boolean applied) {
        this.applied = applied;
    }

    public Instant getAppliedAt() {
        return appliedAt;
    }

    public void setAppliedAt(Instant appliedAt) {
        this.appliedAt = appliedAt;
    }

    public Long getBaseProjectVersion() {
        return baseProjectVersion;
    }

    public void setBaseProjectVersion(Long baseProjectVersion) {
        this.baseProjectVersion = baseProjectVersion;
    }

    public List<ScenarioCreateRequest.ScenarioChangeItem> getChanges() {
        return changes;
    }

    public void setChanges(List<ScenarioCreateRequest.ScenarioChangeItem> changes) {
        this.changes = changes;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
