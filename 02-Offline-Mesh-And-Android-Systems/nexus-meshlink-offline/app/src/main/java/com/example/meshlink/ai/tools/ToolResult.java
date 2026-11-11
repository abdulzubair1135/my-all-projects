package com.example.meshlink.ai.tools;

import java.util.ArrayList;
import java.util.List;

public class ToolResult {
    public final boolean isSuccess;
    public String outputText;
    public final String actionType; // e.g. "NONE", "EMERGENCY_ALERT", "CALL", "SMS", "PPT_DOWNLOAD"
    public final String actionPayload;
    public final List<String> quickChips = new ArrayList<>();
    public String thought;

    public ToolResult(boolean isSuccess, String outputText, String actionType, String actionPayload) {
        this.isSuccess = isSuccess;
        this.outputText = outputText;
        this.actionType = actionType;
        this.actionPayload = actionPayload;
    }

    public static ToolResult text(String output) {
        return new ToolResult(true, output, "NONE", null);
    }

    public static ToolResult action(String output, String actionType, String actionPayload) {
        return new ToolResult(true, output, actionType, actionPayload);
    }

    public ToolResult addChip(String chip) {
        quickChips.add(chip);
        return this;
    }

    public ToolResult setThought(String thought) {
        this.thought = thought;
        return this;
    }
}
