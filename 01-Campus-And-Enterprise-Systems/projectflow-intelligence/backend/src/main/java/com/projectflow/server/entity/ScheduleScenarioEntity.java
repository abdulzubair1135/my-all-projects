package com.projectflow.server.entity;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "schedule_scenarios")
public class ScheduleScenarioEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "project_id", nullable = false)
    private UUID projectId;

    @Column(nullable = false)
    private String name;

    @Column
    private String description;

    @Column(name = "created_by_id", nullable = false)
    private UUID createdById;

    @Column(nullable = false)
    private boolean applied = false;

    @Column(name = "applied_at")
    private Instant appliedAt;

    @Column(name = "base_project_version", nullable = false)
    private Long baseProjectVersion;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();

    public ScheduleScenarioEntity() {
    }

    public ScheduleScenarioEntity(UUID projectId, String name, String description, UUID createdById, Long baseProjectVersion) {
        this.id = UUID.randomUUID();
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

    public Long getBaseProjectVersion() {
        return baseProjectVersion;
    }

    public void setBaseProjectVersion(Long baseProjectVersion) {
        this.baseProjectVersion = baseProjectVersion;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
