package com.projectflow.server.dto;

import java.time.Instant;

public class SystemHealthDto {
    private String status = "UP";
    private String databaseStatus = "CONNECTED";
    private String databaseType;
    private String applicationVersion = "2.0.0";
    private String environment;
    private long uptimeSeconds;
    private long memoryUsedMb;
    private long maxMemoryMb;
    private Instant timestamp = Instant.now();

    public SystemHealthDto() {
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getDatabaseStatus() {
        return databaseStatus;
    }

    public void setDatabaseStatus(String databaseStatus) {
        this.databaseStatus = databaseStatus;
    }

    public String getDatabaseType() {
        return databaseType;
    }

    public void setDatabaseType(String databaseType) {
        this.databaseType = databaseType;
    }

    public String getApplicationVersion() {
        return applicationVersion;
    }

    public void setApplicationVersion(String applicationVersion) {
        this.applicationVersion = applicationVersion;
    }

    public String getEnvironment() {
        return environment;
    }

    public void setEnvironment(String environment) {
        this.environment = environment;
    }

    public long getUptimeSeconds() {
        return uptimeSeconds;
    }

    public void setUptimeSeconds(long uptimeSeconds) {
        this.uptimeSeconds = uptimeSeconds;
    }

    public long getMemoryUsedMb() {
        return memoryUsedMb;
    }

    public void setMemoryUsedMb(long memoryUsedMb) {
        this.memoryUsedMb = memoryUsedMb;
    }

    public long getMaxMemoryMb() {
        return maxMemoryMb;
    }

    public void setMaxMemoryMb(long maxMemoryMb) {
        this.maxMemoryMb = maxMemoryMb;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Instant timestamp) {
        this.timestamp = timestamp;
    }
}
