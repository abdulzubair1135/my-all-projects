package com.projectflow.android.data.local;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "risks")
public class RiskEntity {
    @PrimaryKey
    @NonNull
    public String id;
    public String projectId;
    public String ruleId;
    public String severity;
    public String title;
    public String description;
    public String recommendedAction;
    public String detectedAt;

    public RiskEntity(@NonNull String id, String projectId, String ruleId, String severity, String title, String description, String recommendedAction, String detectedAt) {
        this.id = id;
        this.projectId = projectId;
        this.ruleId = ruleId;
        this.severity = severity;
        this.title = title;
        this.description = description;
        this.recommendedAction = recommendedAction;
        this.detectedAt = detectedAt;
    }
}
