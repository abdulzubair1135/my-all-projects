package com.example.meshlink.data;

public class ChatMessageModel {
    public static final String TYPE_TEXT = "TEXT";
    public static final String TYPE_IMAGE = "IMAGE";
    public static final String TYPE_VIDEO = "VIDEO";
    public static final String TYPE_VOICE = "VOICE";
    public static final String TYPE_FILE = "FILE";
    public static final String TYPE_CALL = "CALL";

    public static final String STATUS_PENDING = "PENDING";
    public static final String STATUS_SENT = "SENT";
    public static final String STATUS_DELIVERED = "DELIVERED";
    public static final String STATUS_SEEN = "SEEN";

    public static final String ROUTE_BLE = "BLE";
    public static final String ROUTE_WIFI_DIRECT = "WIFI_DIRECT";
    public static final String ROUTE_HOTSPOT = "HOTSPOT";

    public String msgId;
    public String sender;
    public String target;
    public String content;
    public long timestamp;
    public String status;
    public String msgType;
    public String mediaPath;
    public String routingMode;
    public int hopCount;

    public ChatMessageModel(String msgId, String sender, String target, String content, long timestamp, String status) {
        this(msgId, sender, target, content, timestamp, status, TYPE_TEXT, "", ROUTE_BLE, 0);
    }

    public ChatMessageModel(String msgId, String sender, String target, String content, long timestamp,
                            String status, String msgType, String mediaPath, String routingMode, int hopCount) {
        this.msgId = msgId;
        this.sender = sender;
        this.target = target;
        this.content = content;
        this.timestamp = timestamp;
        this.status = status;
        this.msgType = msgType != null ? msgType : TYPE_TEXT;
        this.mediaPath = mediaPath != null ? mediaPath : "";
        this.routingMode = routingMode != null ? routingMode : ROUTE_BLE;
        this.hopCount = hopCount;
    }
}
