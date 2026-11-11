package com.projectflow.android.data.local;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "workspaces")
public class WorkspaceEntity {
    @PrimaryKey
    @NonNull
    public String id;
    public String name;
    public String slug;
    public String description;
    public String createdAt;

    public WorkspaceEntity(@NonNull String id, String name, String slug, String description, String createdAt) {
        this.id = id;
        this.name = name;
        this.slug = slug;
        this.description = description;
        this.createdAt = createdAt;
    }
}
