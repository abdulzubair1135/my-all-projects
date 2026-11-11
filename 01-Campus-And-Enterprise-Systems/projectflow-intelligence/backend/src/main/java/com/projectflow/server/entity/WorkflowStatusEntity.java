package com.projectflow.server.entity;

import com.projectflow.core.model.StatusCategory;
import jakarta.persistence.*;
import java.util.UUID;

@Entity
@Table(name = "workflow_statuses", uniqueConstraints = {
        @UniqueConstraint(name = "uq_wf_status_name", columnNames = {"workflow_id", "name"})
})
public class WorkflowStatusEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "workflow_id", nullable = false)
    private UUID workflowId;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String color = "#78866B";

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private StatusCategory category = StatusCategory.TODO;

    @Column(nullable = false)
    private int position = 0;

    public WorkflowStatusEntity() {
    }

    public WorkflowStatusEntity(UUID workflowId, String name, String color, StatusCategory category, int position) {
        this.id = UUID.randomUUID();
        this.workflowId = workflowId;
        this.name = name;
        this.color = color;
        this.category = category;
        this.position = position;
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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public StatusCategory getCategory() {
        return category;
    }

    public void setCategory(StatusCategory category) {
        this.category = category;
    }

    public int getPosition() {
        return position;
    }

    public void setPosition(int position) {
        this.position = position;
    }
}
