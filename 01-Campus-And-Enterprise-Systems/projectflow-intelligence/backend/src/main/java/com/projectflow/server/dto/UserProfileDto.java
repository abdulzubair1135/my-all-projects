package com.projectflow.server.dto;

import com.projectflow.core.model.Role;
import java.time.Instant;
import java.util.UUID;

public class UserProfileDto {
    private UUID id;
    private String email;
    private String fullName;
    private String avatarUrl;
    private Role globalRole;
    private boolean active;
    private Instant createdAt;

    public UserProfileDto() {
    }

    public UserProfileDto(UUID id, String email, String fullName, String avatarUrl, Role globalRole, boolean active, Instant createdAt) {
        this.id = id;
        this.email = email;
        this.fullName = fullName;
        this.avatarUrl = avatarUrl;
        this.globalRole = globalRole;
        this.active = active;
        this.createdAt = createdAt;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getAvatarUrl() {
        return avatarUrl;
    }

    public void setAvatarUrl(String avatarUrl) {
        this.avatarUrl = avatarUrl;
    }

    public Role getGlobalRole() {
        return globalRole;
    }

    public void setGlobalRole(Role globalRole) {
        this.globalRole = globalRole;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
