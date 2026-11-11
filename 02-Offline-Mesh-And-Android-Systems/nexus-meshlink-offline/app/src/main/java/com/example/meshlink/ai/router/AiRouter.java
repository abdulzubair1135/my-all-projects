package com.example.meshlink.ai.router;

public class AiRouter {

    public static ToolCall route(String userInput) {
        if (userInput == null || userInput.trim().isEmpty()) {
            return new ToolCall(UserIntent.GENERAL_QUESTION, false, null, "NORMAL");
        }

        String text = userInput.trim().toLowerCase();

        // 1. CRITICAL: Emergency detection (highest priority)
        if (text.contains("accident") || text.contains("chot") || text.contains("blood") ||
            text.contains("khoon") || text.contains("mar raha") || text.contains("danger") ||
            text.contains("khatra") || text.contains("emergency") || text.contains("madad") ||
            text.contains("cpr") || text.contains("fracture") || text.contains("heart attack")) {
            return new ToolCall(UserIntent.EMERGENCY, true, "emergency_helper", "CRITICAL")
                    .put("query", userInput);
        }

        // 2. Direct Call / SOS Trigger
        if (text.contains("call emergency") || text.contains("call 112") || text.contains("police call") ||
            text.contains("ambulance call")) {
            return new ToolCall(UserIntent.CALL_ACTION, true, "call_helper", "HIGH")
                    .put("number", "112");
        }

        if (text.contains("sos sms") || text.contains("send sms") || text.contains("sms bhejo")) {
            return new ToolCall(UserIntent.SMS_ACTION, true, "sms_helper", "HIGH");
        }

        // 3. Mesh & Offline Network
        if (text.contains("mesh status") || text.contains("mesh me kitne") || text.contains("nearby device") ||
            text.contains("offline node") || text.contains("network status") || text.contains("mesh kaise")) {
            return new ToolCall(UserIntent.MESH_STATUS, true, "mesh_helper", "NORMAL");
        }

        if (text.contains("mesh sos") || text.contains("offline sos")) {
            return new ToolCall(UserIntent.MESH_SOS, true, "emergency_helper", "CRITICAL");
        }

        // 4. Presentations / PPT
        if (text.contains("ppt") || text.contains("presentation") || text.contains("slides") ||
            text.contains("slide deck") || text.contains("pitch deck")) {
            return new ToolCall(UserIntent.CREATE_PRESENTATION, true, "presentation_helper", "NORMAL")
                    .put("topic", userInput);
        }

        // 5. Code & Programming
        if (text.contains("code") || text.contains("program") || text.contains("function") ||
            text.contains("syntax") || text.contains("error") || text.contains("bug") ||
            text.contains("java") || text.contains("python") || text.contains("kotlin") ||
            text.contains("recursion") || text.contains("binary search") || text.contains("fibonacci") ||
            text.contains("loop") || text.contains("class") || text.contains("oops")) {
            return new ToolCall(UserIntent.CODE_HELPER, true, "code_helper", "NORMAL")
                    .put("query", userInput);
        }

        // 6. Live Web Search
        if (text.contains("search") || text.contains("google") || text.contains("latest") ||
            text.contains("today news") || text.contains("current") || text.contains("internet par") ||
            text.contains("find online")) {
            return new ToolCall(UserIntent.WEB_SEARCH, true, "search_tool", "NORMAL")
                    .put("query", userInput);
        }

        // 7. Device Diagnostics
        if (text.contains("ram") || text.contains("device info") || text.contains("storage") ||
            text.contains("battery") || text.contains("hardware") || text.contains("phone capability")) {
            return new ToolCall(UserIntent.DEVICE_STATUS, true, "device_helper", "NORMAL");
        }

        // 8. General Questions & Explanations (handled by Local Brain + Knowledge Base)
        if (text.contains("kya hota") || text.contains("samjhao") || text.contains("explain") ||
            text.contains("kaise") || text.contains("what is") || text.contains("how to")) {
            return new ToolCall(UserIntent.EXPLAIN, false, null, "NORMAL")
                    .put("query", userInput);
        }

        return new ToolCall(UserIntent.GENERAL_QUESTION, false, null, "NORMAL")
                .put("query", userInput);
    }
}
