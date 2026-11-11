package com.cyclecare.models;

import java.io.Serializable;

public class CircleContact implements Serializable {
    private String connection_id;
    private String user_id;
    private String display_name;
    private String cyclecare_id;
    private String relationship;
    private String last_message;
    private String last_message_type;
    private String last_message_time;
    private int unread_count;

    public CircleContact() {}

    public String getConnectionId() { return connection_id; }
    public void setConnectionId(String connection_id) { this.connection_id = connection_id; }

    public String getUserId() { return user_id; }
    public void setUserId(String user_id) { this.user_id = user_id; }

    public String getDisplayName() { return display_name != null ? display_name : "Circle Contact"; }
    public void setDisplayName(String display_name) { this.display_name = display_name; }

    public String getCyclecareId() { return cyclecare_id != null ? cyclecare_id : "@circle"; }
    public void setCyclecareId(String cyclecare_id) { this.cyclecare_id = cyclecare_id; }

    public String getRelationship() { return relationship != null ? relationship : "Partner"; }
    public void setRelationship(String relationship) { this.relationship = relationship; }

    public String getLastMessage() { return last_message != null ? last_message : ""; }
    public void setLastMessage(String last_message) { this.last_message = last_message; }

    public String getLastMessageType() { return last_message_type != null ? last_message_type : "TEXT"; }
    public void setLastMessageType(String last_message_type) { this.last_message_type = last_message_type; }

    public String getLastMessageTime() { return last_message_time; }
    public void setLastMessageTime(String last_message_time) { this.last_message_time = last_message_time; }

    public int getUnreadCount() { return unread_count; }
    public void setUnreadCount(int unread_count) { this.unread_count = unread_count; }
}
