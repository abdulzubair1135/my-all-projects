package com.projectflow.android.data.local;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "projects")
public class ProjectEntity {
    @PrimaryKey
    @NonNull
    public String id;
    public String workspaceId;
    public String name;
    public String code;
    public String description;
    public String status;
    public String health;
    public String targetDate;
    public String assigneeId;
    public String assigneeName;
    public String assigneeEmail;
    public String teamId;
    public String teamName;

    @androidx.room.Ignore
    public ProjectEntity() {}

    @androidx.room.Ignore
    public ProjectEntity(@NonNull String id, String workspaceId, String name, String code, String description, String status, String health, String targetDate) {
        this(id, workspaceId, name, code, description, status, health, targetDate, null, null, null, null, null);
    }

    public ProjectEntity(@NonNull String id, String workspaceId, String name, String code, String description, String status, String health, String targetDate, String assigneeId, String assigneeName, String assigneeEmail, String teamId, String teamName) {
        this.id = id;
        this.workspaceId = workspaceId;
        this.name = name;
        this.code = code;
        this.description = description;
        this.status = status;
        this.health = health;
        this.targetDate = targetDate;
        this.assigneeId = assigneeId;
        this.assigneeName = assigneeName;
        this.assigneeEmail = assigneeEmail;
        this.teamId = teamId;
        this.teamName = teamName;
    }
}
