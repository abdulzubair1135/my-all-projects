package com.projectflow.server.dto;

import jakarta.validation.constraints.NotBlank;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class ScenarioCreateRequest {

    @NotBlank(message = "Scenario name is required")
    private String name;

    private String description;
    private List<ScenarioChangeItem> changes = new ArrayList<>();

    public ScenarioCreateRequest() {
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

    public List<ScenarioChangeItem> getChanges() {
        return changes;
    }

    public void setChanges(List<ScenarioChangeItem> changes) {
        this.changes = changes;
    }

    public static class ScenarioChangeItem {
        private UUID taskId;
        private LocalDate proposedDueDate;
        private BigDecimal proposedEstimatedHours;
        private UUID proposedAssigneeId;

        public ScenarioChangeItem() {
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
}
