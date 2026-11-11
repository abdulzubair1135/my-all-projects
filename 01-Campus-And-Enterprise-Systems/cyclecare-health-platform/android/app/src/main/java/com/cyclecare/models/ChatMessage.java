package com.cyclecare.models;

import java.io.Serializable;
import java.util.Map;

public class ChatMessage implements Serializable {
    private String id;
    private String connection_id;
    private String sender_id;
    private String receiver_id;
    private String message_type; // 'TEXT', 'CARE_REQUEST', 'CARE_ITEM_SENT', 'EMERGENCY_SOS'
    private String content;
    private Map<String, Object> metadata;
    private boolean is_read;
    private String created_at;
    private boolean is_mine;

    public ChatMessage() {}

    public ChatMessage(String id, String content, boolean is_mine, String message_type) {
        this.id = id;
        this.content = content;
        this.is_mine = is_mine;
        this.message_type = message_type;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getConnectionId() { return connection_id; }
    public void setConnectionId(String connection_id) { this.connection_id = connection_id; }

    public String getSenderId() { return sender_id; }
    public void setSenderId(String sender_id) { this.sender_id = sender_id; }

    public String getReceiverId() { return receiver_id; }
    public void setReceiverId(String receiver_id) { this.receiver_id = receiver_id; }

    public String getMessageType() { return message_type != null ? message_type : "TEXT"; }
    public void setMessageType(String message_type) { this.message_type = message_type; }

    public String getContent() { return content != null ? content : ""; }
    public void setContent(String content) { this.content = content; }

    public Map<String, Object> getMetadata() { return metadata; }
    public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }

    public boolean isRead() { return is_read; }
    public void setRead(boolean read) { is_read = read; }

    public String getCreatedAt() { return created_at; }
    public void setCreatedAt(String created_at) { this.created_at = created_at; }

    public boolean isMine() { return is_mine; }
    public void setMine(boolean mine) { is_mine = mine; }

    // Helpers for attached care / medical item metadata
    public String getItemName() {
        if (metadata != null && metadata.containsKey("item_name")) {
            return String.valueOf(metadata.get("item_name"));
        }
        return null;
    }

    public String getItemCategory() {
        if (metadata != null && metadata.containsKey("item_category")) {
            return String.valueOf(metadata.get("item_category"));
        }
        return "Care Essential";
    }

    public int getItemPrice() {
        if (metadata != null && metadata.containsKey("item_price")) {
            Object p = metadata.get("item_price");
            if (p instanceof Number) return ((Number) p).intValue();
            try { return (int) Double.parseDouble(String.valueOf(p)); } catch (Exception ignored) {}
        }
        return 199;
    }

    public String getItemImage() {
        if (metadata != null && metadata.containsKey("item_image")) {
            return String.valueOf(metadata.get("item_image"));
        }
        return null;
    }

    public String getItemStatus() {
        if (metadata != null && metadata.containsKey("status")) {
            return String.valueOf(metadata.get("status"));
        }
        return "REQUESTED";
    }
}
