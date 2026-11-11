package com.projectflow.server.dto;

import jakarta.validation.constraints.NotNull;
import java.util.UUID;

public class TaskTransitionRequest {

    @NotNull(message = "Target status ID is required")
    private UUID targetStatusId;

    public TaskTransitionRequest() {
    }

    public TaskTransitionRequest(UUID targetStatusId) {
        this.targetStatusId = targetStatusId;
    }

    public UUID getTargetStatusId() {
        return targetStatusId;
    }

    public void setTargetStatusId(UUID targetStatusId) {
        this.targetStatusId = targetStatusId;
    }
}
