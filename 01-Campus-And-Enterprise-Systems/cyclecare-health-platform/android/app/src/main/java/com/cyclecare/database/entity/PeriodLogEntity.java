package com.cyclecare.database.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "local_period_logs")
public class PeriodLogEntity {
    @PrimaryKey
    @NonNull
    private String id;

    private String startDate;
    private String endDate;
    private String flow;
    private String notes;
    private boolean isSynced;

    public PeriodLogEntity(@NonNull String id, String startDate, String endDate, String flow, String notes, boolean isSynced) {
        this.id = id;
        this.startDate = startDate;
        this.endDate = endDate;
        this.flow = flow;
        this.notes = notes;
        this.isSynced = isSynced;
    }

    @NonNull
    public String getId() { return id; }
    public String getStartDate() { return startDate; }
    public String getEndDate() { return endDate; }
    public String getFlow() { return flow; }
    public String getNotes() { return notes; }
    public boolean isSynced() { return isSynced; }
    public void setSynced(boolean synced) { isSynced = synced; }
}
