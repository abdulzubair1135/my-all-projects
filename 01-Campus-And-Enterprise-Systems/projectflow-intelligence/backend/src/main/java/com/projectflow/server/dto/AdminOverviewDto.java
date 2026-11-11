package com.projectflow.server.dto;

import java.time.Instant;

public class AdminOverviewDto {
    private long totalUsers;
    private long activeUsers;
    private long totalOrganizations;
    private long totalWorkspaces;
    private long totalProjects;
    private long totalTasks;
    private long completedTasks;
    private long activeRisks;
    private long syncFailures;
    private String systemStatus = "OPERATIONAL";
    private Instant calculatedAt = Instant.now();

    public AdminOverviewDto() {
    }

    public long getTotalUsers() {
        return totalUsers;
    }

    public void setTotalUsers(long totalUsers) {
        this.totalUsers = totalUsers;
    }

    public long getActiveUsers() {
        return activeUsers;
    }

    public void setActiveUsers(long activeUsers) {
        this.activeUsers = activeUsers;
    }

    public long getTotalOrganizations() {
        return totalOrganizations;
    }

    public void setTotalOrganizations(long totalOrganizations) {
        this.totalOrganizations = totalOrganizations;
    }

    public long getTotalWorkspaces() {
        return totalWorkspaces;
    }

    public void setTotalWorkspaces(long totalWorkspaces) {
        this.totalWorkspaces = totalWorkspaces;
    }

    public long getTotalProjects() {
        return totalProjects;
    }

    public void setTotalProjects(long totalProjects) {
        this.totalProjects = totalProjects;
    }

    public long getTotalTasks() {
        return totalTasks;
    }

    public void setTotalTasks(long totalTasks) {
        this.totalTasks = totalTasks;
    }

    public long getCompletedTasks() {
        return completedTasks;
    }

    public void setCompletedTasks(long completedTasks) {
        this.completedTasks = completedTasks;
    }

    public long getActiveRisks() {
        return activeRisks;
    }

    public void setActiveRisks(long activeRisks) {
        this.activeRisks = activeRisks;
    }

    public long getSyncFailures() {
        return syncFailures;
    }

    public void setSyncFailures(long syncFailures) {
        this.syncFailures = syncFailures;
    }

    public String getSystemStatus() {
        return systemStatus;
    }

    public void setSystemStatus(String systemStatus) {
        this.systemStatus = systemStatus;
    }

    public Instant getCalculatedAt() {
        return calculatedAt;
    }

    public void setCalculatedAt(Instant calculatedAt) {
        this.calculatedAt = calculatedAt;
    }
}
