package com.projectflow.android.data.local;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "sync_queue")
public class SyncQueueEntity {
    @PrimaryKey
    @NonNull
    public String id;
    public String operationType;
    public String entityType;
    public String entityId;
    public String payloadJson;
    public String status;
    public String createdAt;

    public SyncQueueEntity(@NonNull String id, String operationType, String entityType, String entityId, String payloadJson, String status, String createdAt) {
        this.id = id;
        this.operationType = operationType;
        this.entityType = entityType;
        this.entityId = entityId;
        this.payloadJson = payloadJson;
        this.status = status;
        this.createdAt = createdAt;
    }
}
