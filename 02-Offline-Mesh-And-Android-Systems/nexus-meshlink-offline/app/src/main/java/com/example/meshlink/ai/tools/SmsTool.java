package com.example.meshlink.ai.tools;

import android.content.Intent;
import android.net.Uri;

public class SmsTool {

    public static ToolResult prepareSosSms(double lat, double lng) {
        String locationUrl = (lat != 0 && lng != 0) ?
                "https://maps.google.com/?q=" + lat + "," + lng : "Location Unavailable";

        String smsBody = "SOS EMERGENCY ALERT!\nI need immediate assistance.\nMy coordinates: " +
                lat + ", " + lng + "\nLive Map: " + locationUrl + "\nSent via Nexus MeshLink.";

        String message = "📨 **SOS SMS Prepared:**\n\n```\n" + smsBody + "\n```\n" +
                "Kripya recipient number select karein aur send confirm karein.";

        return ToolResult.action(message, "SMS", smsBody)
                .addChip("📨 Send SOS SMS")
                .addChip("Cancel");
    }

    public static Intent getSmsIntent(String body) {
        Intent intent = new Intent(Intent.ACTION_SENDTO);
        intent.setData(Uri.parse("smsto:"));
        intent.putExtra("sms_body", body);
        return intent;
    }
}
