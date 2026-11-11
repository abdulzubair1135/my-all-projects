package com.projectflow.android.data.model;

public class ConversationItem {
    public enum Type { DIRECT, GROUP }

    public String id; // channel identifier (e.g. dm_user1_user2 or group_...)
    public String title;
    public String snippet;
    public String time;
    public String initial;
    public Type type;
    public int memberCount;
    public boolean online;
    public String targetEmail;

    public ConversationItem(String id, String title, String snippet, String time, String initial, Type type, boolean online) {
        this.id = id;
        this.title = title;
        this.snippet = snippet;
        this.time = time;
        this.initial = initial;
        this.type = type;
        this.online = online;
    }
}
