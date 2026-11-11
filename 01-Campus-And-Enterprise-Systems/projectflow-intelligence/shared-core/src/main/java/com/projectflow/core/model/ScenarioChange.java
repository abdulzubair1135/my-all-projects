package com.projectflow.core.model;

import java.time.LocalDate;
import java.util.UUID;

public class ScenarioChange {
    private UUID id;
    private UUID scenarioId;
    private UUID taskId;
    private LocalDate proposedDueDate;
    private Double proposedEstimatedHours;
    private UUID proposedAssigneeId;

    public ScenarioChange() {
    }

    public ScenarioChange(UUID id, UUID scenarioId, UUID taskId, LocalDate proposedDueDate, Double proposedEstimatedHours, UUID proposedAssigneeId) {
        this.id = id;
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

    public Double getProposedEstimatedHours() {
        return proposedEstimatedHours;
    }

    public void setProposedEstimatedHours(Double proposedEstimatedHours) {
        this.proposedEstimatedHours = proposedEstimatedHours;
    }

    public UUID getProposedAssigneeId() {
        return proposedAssigneeId;
    }

    public void setProposedAssigneeId(UUID proposedAssigneeId) {
        this.proposedAssigneeId = proposedAssigneeId;
    }
}
