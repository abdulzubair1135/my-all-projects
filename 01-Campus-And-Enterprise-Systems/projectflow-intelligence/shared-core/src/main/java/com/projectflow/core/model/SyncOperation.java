package com.projectflow.core.model;

import java.time.Instant;
import java.util.UUID;

public class SyncOperation {
    private UUID id;
    private String clientOperationId;
    private String entityType;
    private UUID entityId;
    private OperationType operationType;
    private String payloadJson;
    private long baseVersion;
    private Instant clientCreatedAt;
    private int retryCount;
    private String status; // PENDING, SYNCED, CONFLICT, FAILED
    private String errorMessage;

    public SyncOperation() {
    }

    public SyncOperation(UUID id, String clientOperationId, String entityType, UUID entityId,
                         OperationType operationType, String payloadJson, long baseVersion) {
        this.id = id;
        this.clientOperationId = clientOperationId;
        this.entityType = entityType;
        this.entityId = entityId;
        this.operationType = operationType;
        this.payloadJson = payloadJson;
        this.baseVersion = baseVersion;
        this.clientCreatedAt = Instant.now();
        this.retryCount = 0;
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

    public long getBaseVersion() {
        return baseVersion;
    }

    public void setBaseVersion(long baseVersion) {
        this.baseVersion = baseVersion;
    }

    public Instant getClientCreatedAt() {
        return clientCreatedAt;
    }

    public void setClientCreatedAt(Instant clientCreatedAt) {
        this.clientCreatedAt = clientCreatedAt;
    }

    public int getRetryCount() {
        return retryCount;
    }

    public void setRetryCount(int retryCount) {
        this.retryCount = retryCount;
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
}
