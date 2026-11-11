package com.projectflow.server.dto;

import com.projectflow.core.model.OperationType;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class SyncBatchRequest {
    private List<SyncItem> operations = new ArrayList<>();

    public SyncBatchRequest() {
    }

    public SyncBatchRequest(List<SyncItem> operations) {
        this.operations = operations;
    }

    public List<SyncItem> getOperations() {
        return operations;
    }

    public void setOperations(List<SyncItem> operations) {
        this.operations = operations;
    }

    public static class SyncItem {
        private String clientOperationId;
        private String entityType;
        private UUID entityId;
        private OperationType operationType;
        private String payloadJson;
        private long baseVersion;
        private Instant clientCreatedAt;

        public SyncItem() {
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
    }
}
