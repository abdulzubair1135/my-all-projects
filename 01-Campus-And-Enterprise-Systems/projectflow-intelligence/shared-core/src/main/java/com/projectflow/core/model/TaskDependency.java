package com.projectflow.core.model;

import java.util.UUID;

public class TaskDependency {
    private UUID id;
    private UUID taskId;
    private UUID predecessorTaskId;
    private String dependencyType;

    public TaskDependency() {
    }

    public TaskDependency(UUID id, UUID taskId, UUID predecessorTaskId) {
        this.id = id;
        this.taskId = taskId;
        this.predecessorTaskId = predecessorTaskId;
        this.dependencyType = "FINISH_TO_START";
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getTaskId() {
        return taskId;
    }

    public void setTaskId(UUID taskId) {
        this.taskId = taskId;
    }

    public UUID getPredecessorTaskId() {
        return predecessorTaskId;
    }

    public void setPredecessorTaskId(UUID predecessorTaskId) {
        this.predecessorTaskId = predecessorTaskId;
    }

    public String getDependencyType() {
        return dependencyType;
    }

    public void setDependencyType(String dependencyType) {
        this.dependencyType = dependencyType;
    }
}
