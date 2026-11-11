package com.example.meshlink.data;

public class ContactModel {
    public String peerId;
    public String displayName;
    public String avatarEmoji;
    public String lastMessage;
    public long lastTimestamp;
    public int unreadCount;
    public boolean isOnline;
    public String transportType; // BLE, WIFI_DIRECT, HOTSPOT
    public String ipAddress;

    public ContactModel(String peerId, String displayName, String avatarEmoji, String lastMessage,
                        long lastTimestamp, int unreadCount, boolean isOnline, String transportType) {
        this.peerId = peerId;
        this.displayName = displayName;
        this.avatarEmoji = avatarEmoji;
        this.lastMessage = lastMessage;
        this.lastTimestamp = lastTimestamp;
        this.unreadCount = unreadCount;
        this.isOnline = isOnline;
        this.transportType = transportType;
    }
}
