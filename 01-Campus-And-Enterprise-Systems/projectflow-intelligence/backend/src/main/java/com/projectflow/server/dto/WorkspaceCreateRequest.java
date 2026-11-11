package com.projectflow.server.dto;

import jakarta.validation.constraints.NotBlank;
import java.util.UUID;

public class WorkspaceCreateRequest {

    private UUID organizationId;

    @NotBlank(message = "Workspace name is required")
    private String name;

    private String slug;
    private String description;

    public WorkspaceCreateRequest() {
    }

    public WorkspaceCreateRequest(UUID organizationId, String name, String slug, String description) {
        this.organizationId = organizationId;
        this.name = name;
        this.slug = slug;
        this.description = description;
    }

    public UUID getOrganizationId() {
        return organizationId;
    }

    public void setOrganizationId(UUID organizationId) {
        this.organizationId = organizationId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getSlug() {
        return slug;
    }

    public void setSlug(String slug) {
        this.slug = slug;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
