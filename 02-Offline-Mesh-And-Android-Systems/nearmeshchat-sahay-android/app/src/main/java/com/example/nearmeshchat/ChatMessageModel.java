package com.example.nearmeshchat;

public class ChatMessageModel {
    public String msgId;
    public String sender;
    public String target;
    public String content;
    public long timestamp;
    public String status; // PENDING, DELIVERED, SEEN

    public ChatMessageModel(String msgId, String sender, String target, String content, long timestamp, String status) {
        this.msgId = msgId;
        this.sender = sender;
        this.target = target;
        this.content = content;
        this.timestamp = timestamp;
        this.status = status;
    }
}