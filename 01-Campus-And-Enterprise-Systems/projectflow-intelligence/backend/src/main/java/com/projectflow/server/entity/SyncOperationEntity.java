package com.projectflow.server.entity;

import com.projectflow.core.model.OperationType;
import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "sync_operations")
public class SyncOperationEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "client_operation_id", nullable = false, unique = true)
    private String clientOperationId;

    @Column(name = "entity_type", nullable = false)
    private String entityType;

    @Column(name = "entity_id", nullable = false)
    private UUID entityId;

    @Enumerated(EnumType.STRING)
    @Column(name = "operation_type", nullable = false)
    private OperationType operationType;

    @Column(name = "payload_json", nullable = false, length = 4000)
    private String payloadJson;

    @Column(name = "base_version", nullable = false)
    private Long baseVersion;

    @Column(nullable = false)
    private String status = "PENDING";

    @Column(name = "error_message")
    private String errorMessage;

    @Column(name = "client_created_at", nullable = false)
    private Instant clientCreatedAt;

    @Column(name = "processed_at")
    private Instant processedAt;

    public SyncOperationEntity() {
    }

    public SyncOperationEntity(String clientOperationId, String entityType, UUID entityId, OperationType operationType, String payloadJson, Long baseVersion, Instant clientCreatedAt) {
        this.id = UUID.randomUUID();
        this.clientOperationId = clientOperationId;
        this.entityType = entityType;
        this.entityId = entityId;
        this.operationType = operationType;
        this.payloadJson = payloadJson;
        this.baseVersion = baseVersion;
        this.clientCreatedAt = clientCreatedAt != null ? clientCreatedAt : Instant.now();
        this.status = "PENDING";
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getClientOperationId() {
        return clientOperationId;
    }

    public void setClientOperationId(String clientOperationId) {
        this.clientOperationId = clientOperationId;
    }

    public String getEntityType() {
        return entityType;
    }

    public void setEntityType(String entityType) {
        this.entityType = entityType;
    }

    public UUID getEntityId() {
        return entityId;
    }

    public void setEntityId(UUID entityId) {
        this.entityId = entityId;
    }

    public OperationType getOperationType() {
        return operationType;
    }

    public void setOperationType(OperationType operationType) {
        this.operationType = operationType;
    }

    public String getPayloadJson() {
        return payloadJson;
    }

    public void setPayloadJson(String payloadJson) {
        this.payloadJson = payloadJson;
    }

    public Long getBaseVersion() {
        return baseVersion;
    }

    public void setBaseVersion(Long baseVersion) {
        this.baseVersion = baseVersion;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public Instant getClientCreatedAt() {
        return clientCreatedAt;
    }

    public void setClientCreatedAt(Instant clientCreatedAt) {
        this.clientCreatedAt = clientCreatedAt;
    }

    public Instant getProcessedAt() {
        return processedAt;
    }

    public void setProcessedAt(Instant processedAt) {
        this.processedAt = processedAt;
    }
}
