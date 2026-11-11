package com.example.meshlink.data;

public class CallModel {
    public static final String TYPE_VOICE = "VOICE";
    public static final String TYPE_VIDEO = "VIDEO";

    public static final String DIR_OUTGOING = "OUTGOING";
    public static final String DIR_INCOMING = "INCOMING";
    public static final String DIR_MISSED = "MISSED";

    public String callId;
    public String peerId;
    public String peerName;
    public String callType;      // VOICE or VIDEO
    public String direction;     // OUTGOING, INCOMING, MISSED
    public int durationSeconds;
    public long timestamp;
    public String transport;     // WIFI_DIRECT or HOTSPOT

    public CallModel(String callId, String peerId, String peerName, String callType,
                     String direction, int durationSeconds, long timestamp, String transport) {
        this.callId = callId;
        this.peerId = peerId;
        this.peerName = peerName;
        this.callType = callType;
        this.direction = direction;
        this.durationSeconds = durationSeconds;
        this.timestamp = timestamp;
        this.transport = transport;
    }
}
