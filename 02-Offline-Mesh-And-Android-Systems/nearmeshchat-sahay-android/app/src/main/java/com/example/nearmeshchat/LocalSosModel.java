package com.example.nearmeshchat;

public class LocalSosModel {
    public String eventId;
    public String originDeviceId;
    public String userId;
    public String userName;
    public String userPhone;
    public String type;
    public String severity;
    public String description;
    public int peopleCount;
    public int injuredCount;
    public double latitude;
    public double longitude;
    public float accuracy;
    public String status;
    public String source;
    public int hopCount;
    public String relayPath;
    public long createdAt;
    public boolean synced;

    public LocalSosModel() {}

    public LocalSosModel(String eventId, String originDeviceId, String userId, String userName, String userPhone,
                         String type, String severity, String description, int peopleCount, int injuredCount,
                         double latitude, double longitude, float accuracy, String status, String source,
                         int hopCount, String relayPath, long createdAt, boolean synced) {
        this.eventId = eventId;
        this.originDeviceId = originDeviceId;
        this.userId = userId;
        this.userName = userName;
        this.userPhone = userPhone;
        this.type = type;
        this.severity = severity;
        this.description = description;
        this.peopleCount = peopleCount;
        this.injuredCount = injuredCount;
        this.latitude = latitude;
        this.longitude = longitude;
        this.accuracy = accuracy;
        this.status = status;
        this.source = source;
        this.hopCount = hopCount;
        this.relayPath = relayPath;
        this.createdAt = createdAt;
        this.synced = synced;
    }
}