package com.projectflow.server.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "scenario_changes")
public class ScenarioChangeEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "scenario_id", nullable = false)
    private UUID scenarioId;

    @Column(name = "task_id", nullable = false)
    private UUID taskId;

    @Column(name = "proposed_due_date")
    private LocalDate proposedDueDate;

    @Column(name = "proposed_estimated_hours", precision = 6, scale = 2)
    private BigDecimal proposedEstimatedHours;

    @Column(name = "proposed_assignee_id")
    private UUID proposedAssigneeId;

    public ScenarioChangeEntity() {
    }

    public ScenarioChangeEntity(UUID scenarioId, UUID taskId, LocalDate proposedDueDate, BigDecimal proposedEstimatedHours, UUID proposedAssigneeId) {
        this.id = UUID.randomUUID();
        this.scenarioId = scenarioId;
        this.taskId = taskId;
        this.proposedDueDate = proposedDueDate;
        this.proposedEstimatedHours = proposedEstimatedHours;
        this.proposedAssigneeId = proposedAssigneeId;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getScenarioId() {
        return scenarioId;
    }

    public void setScenarioId(UUID scenarioId) {
        this.scenarioId = scenarioId;
    }

    public UUID getTaskId() {
        return taskId;
    }

    public void setTaskId(UUID taskId) {
        this.taskId = taskId;
    }

    public LocalDate getProposedDueDate() {
        return proposedDueDate;
    }

    public void setProposedDueDate(LocalDate proposedDueDate) {
        this.proposedDueDate = proposedDueDate;
    }

    public BigDecimal getProposedEstimatedHours() {
        return proposedEstimatedHours;
    }

    public void setProposedEstimatedHours(BigDecimal proposedEstimatedHours) {
        this.proposedEstimatedHours = proposedEstimatedHours;
    }

    public UUID getProposedAssigneeId() {
        return proposedAssigneeId;
    }

    public void setProposedAssigneeId(UUID proposedAssigneeId) {
        this.proposedAssigneeId = proposedAssigneeId;
    }
}
