package com.example.meshlink.ai.router;

import java.util.HashMap;
import java.util.Map;

public class ToolCall {
    public final UserIntent intent;
    public final boolean requiresTool;
    public final String toolName;
    public final String priority; // "NORMAL", "HIGH", "CRITICAL"
    public final Map<String, String> params = new HashMap<>();

    public ToolCall(UserIntent intent, boolean requiresTool, String toolName, String priority) {
        this.intent = intent;
        this.requiresTool = requiresTool;
        this.toolName = toolName;
        this.priority = priority;
    }

    public ToolCall put(String key, String value) {
        params.put(key, value);
        return this;
    }

    public String get(String key, String defaultValue) {
        return params.containsKey(key) ? params.get(key) : defaultValue;
    }
}
