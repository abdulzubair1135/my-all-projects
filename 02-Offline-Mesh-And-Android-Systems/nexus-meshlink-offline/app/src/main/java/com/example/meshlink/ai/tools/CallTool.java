package com.example.meshlink.ai.tools;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;

public class CallTool {

    public static ToolResult prepareCall(String number) {
        String targetNumber = (number != null && !number.trim().isEmpty()) ? number : "112";
        String message = "📞 **Emergency Call Preparation:**\n\n" +
                "Target Number: `" + targetNumber + "`\n" +
                "Android security guidelines ke according, phone call user confirmation ke baad hi lagayi jayegi.";

        return ToolResult.action(message, "CALL", targetNumber)
                .addChip("📞 Call " + targetNumber)
                .addChip("Cancel");
    }

    public static Intent getDialIntent(String number) {
        String num = (number != null && !number.isEmpty()) ? number : "112";
        return new Intent(Intent.ACTION_DIAL, Uri.parse("tel:" + num));
    }
}
