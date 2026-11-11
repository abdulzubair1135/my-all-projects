package com.example.meshlink.ai.ui;

import java.util.ArrayList;
import java.util.List;

public class AiMessage {
    public String text;
    public String thought;
    public final boolean isUser;
    public final long timestamp;
    public String actionType;
    public String actionPayload;
    public final List<String> chips = new ArrayList<>();
    public boolean isThinking = false;
    public boolean isThoughtExpanded = true;

    public AiMessage(String text, boolean isUser) {
        this(text, isUser, "NONE", null);
    }

    public AiMessage(String text, boolean isUser, boolean isThinking) {
        this(text, isUser, "NONE", null);
        this.isThinking = isThinking;
    }

    public AiMessage(String text, boolean isUser, String actionType, String actionPayload) {
        this.text = text;
        this.isUser = isUser;
        this.timestamp = System.currentTimeMillis();
        this.actionType = actionType;
        this.actionPayload = actionPayload;
    }

    public AiMessage addChips(List<String> newChips) {
        if (newChips != null) {
            this.chips.addAll(newChips);
        }
        return this;
    }
}
