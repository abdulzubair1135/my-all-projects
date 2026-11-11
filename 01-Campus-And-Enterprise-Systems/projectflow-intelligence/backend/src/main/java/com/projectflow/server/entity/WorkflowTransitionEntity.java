package com.projectflow.server.entity;

import jakarta.persistence.*;
import java.util.UUID;

@Entity
@Table(name = "workflow_transitions", uniqueConstraints = {
        @UniqueConstraint(name = "uq_wf_transition", columnNames = {"workflow_id", "from_status_id", "to_status_id"})
})
public class WorkflowTransitionEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "workflow_id", nullable = false)
    private UUID workflowId;

    @Column(name = "from_status_id")
    private UUID fromStatusId;

    @Column(name = "to_status_id", nullable = false)
    private UUID toStatusId;

    @Column
    private String name;

    public WorkflowTransitionEntity() {
    }

    public WorkflowTransitionEntity(UUID workflowId, UUID fromStatusId, UUID toStatusId, String name) {
        this.id = UUID.randomUUID();
        this.workflowId = workflowId;
        this.fromStatusId = fromStatusId;
        this.toStatusId = toStatusId;
        this.name = name;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getWorkflowId() {
        return workflowId;
    }

    public void setWorkflowId(UUID workflowId) {
        this.workflowId = workflowId;
    }

    public UUID getFromStatusId() {
        return fromStatusId;
    }

    public void setFromStatusId(UUID fromStatusId) {
        this.fromStatusId = fromStatusId;
    }

    public UUID getToStatusId() {
        return toStatusId;
    }

    public void setToStatusId(UUID toStatusId) {
        this.toStatusId = toStatusId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
