package com.example.meshlink.ai.context;

import java.util.ArrayList;
import java.util.List;

public class ContextManager {

    private static final int MAX_MESSAGES_BATTERY = 4;
    private static final int MAX_MESSAGES_BALANCED = 8;
    private static final int MAX_MESSAGES_PERFORMANCE = 16;

    public static class ChatTurn {
        public final boolean isUser;
        public final String content;

        public ChatTurn(boolean isUser, String content) {
            this.isUser = isUser;
            this.content = content;
        }
    }

    private final List<ChatTurn> history = new ArrayList<>();

    public synchronized void addMessage(boolean isUser, String content) {
        history.add(new ChatTurn(isUser, content));
    }

    public synchronized void prune(String aiMode) {
        int max = MAX_MESSAGES_BALANCED;
        if ("battery".equalsIgnoreCase(aiMode)) max = MAX_MESSAGES_BATTERY;
        else if ("performance".equalsIgnoreCase(aiMode)) max = MAX_MESSAGES_PERFORMANCE;

        while (history.size() > max) {
            history.remove(0);
        }
    }

    public synchronized List<ChatTurn> getRecentHistory() {
        return new ArrayList<>(history);
    }

    public synchronized void clear() {
        history.clear();
    }
}
