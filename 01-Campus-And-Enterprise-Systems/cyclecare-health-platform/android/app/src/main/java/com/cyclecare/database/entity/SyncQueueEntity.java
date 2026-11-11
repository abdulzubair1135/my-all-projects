package com.cyclecare.database.entity;

import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "sync_queue")
public class SyncQueueEntity {
    @PrimaryKey(autoGenerate = true)
    private int id;

    private String actionType; // ADD_PERIOD, SYMPTOM_LOG, MOOD_LOG
    private String payloadJson;
    private long createdAt;

    public SyncQueueEntity(String actionType, String payloadJson, long createdAt) {
        this.actionType = actionType;
        this.payloadJson = payloadJson;
        this.createdAt = createdAt;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public String getActionType() { return actionType; }
    public String getPayloadJson() { return payloadJson; }
    public long getCreatedAt() { return createdAt; }
}
