package com.projectflow.core.model;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class ScheduleScenario {
    private UUID id;
    private UUID projectId;
    private String name;
    private String description;
    private UUID createdById;
    private boolean applied;
    private Instant appliedAt;
    private long baseProjectVersion;
    private List<ScenarioChange> changes = new ArrayList<>();
    private Instant createdAt;

    public ScheduleScenario() {
    }

    public ScheduleScenario(UUID id, UUID projectId, String name, String description, UUID createdById, long baseProjectVersion) {
        this.id = id;
        this.projectId = projectId;
        this.name = name;
        this.description = description;
        this.createdById = createdById;
        this.baseProjectVersion = baseProjectVersion;
        this.applied = false;
        this.createdAt = Instant.now();
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

    public long getBaseProjectVersion() {
        return baseProjectVersion;
    }

    public void setBaseProjectVersion(long baseProjectVersion) {
        this.baseProjectVersion = baseProjectVersion;
    }

    public List<ScenarioChange> getChanges() {
        return changes;
    }

    public void setChanges(List<ScenarioChange> changes) {
        this.changes = changes;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
