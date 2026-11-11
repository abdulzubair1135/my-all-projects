package com.projectflow.server.entity;

import jakarta.persistence.*;
import java.util.UUID;

@Entity
@Table(name = "task_dependencies", uniqueConstraints = {
        @UniqueConstraint(name = "uq_task_dep", columnNames = {"task_id", "predecessor_task_id"})
})
public class TaskDependencyEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "task_id", nullable = false)
    private UUID taskId;

    @Column(name = "predecessor_task_id", nullable = false)
    private UUID predecessorTaskId;

    @Column(name = "dependency_type", nullable = false)
    private String dependencyType = "FINISH_TO_START";

    public TaskDependencyEntity() {
    }

    public TaskDependencyEntity(UUID taskId, UUID predecessorTaskId) {
        this.id = UUID.randomUUID();
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
