package com.projectflow.server.dto;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

public class SyncBatchResponse {
    private List<SyncResultItem> results = new ArrayList<>();
    private Instant processedAt = Instant.now();

    public SyncBatchResponse() {
    }

    public SyncBatchResponse(List<SyncResultItem> results) {
        this.results = results;
        this.processedAt = Instant.now();
    }

    public List<SyncResultItem> getResults() {
        return results;
    }

    public void setResults(List<SyncResultItem> results) {
        this.results = results;
    }

    public Instant getProcessedAt() {
        return processedAt;
    }

    public void setProcessedAt(Instant processedAt) {
        this.processedAt = processedAt;
    }

    public static class SyncResultItem {
        private String clientOperationId;
        private String status; // SYNCED, CONFLICT, FAILED, DUPLICATE_IGNORED
        private Long currentServerVersion;
        private String message;

        public SyncResultItem() {
        }

        public SyncResultItem(String clientOperationId, String status, Long currentServerVersion, String message) {
            this.clientOperationId = clientOperationId;
            this.status = status;
            this.currentServerVersion = currentServerVersion;
            this.message = message;
        }

        public String getClientOperationId() {
            return clientOperationId;
        }

        public void setClientOperationId(String clientOperationId) {
            this.clientOperationId = clientOperationId;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public Long getCurrentServerVersion() {
            return currentServerVersion;
        }

        public void setCurrentServerVersion(Long currentServerVersion) {
            this.currentServerVersion = currentServerVersion;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }
    }
}
