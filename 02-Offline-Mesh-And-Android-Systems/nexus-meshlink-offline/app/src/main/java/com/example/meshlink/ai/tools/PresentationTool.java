package com.example.meshlink.ai.tools;

public class PresentationTool {

    public static ToolResult generatePresentation(String prompt) {
        String topic = extractTopic(prompt);
        StringBuilder sb = new StringBuilder();

        sb.append("📊 **PRESENTATION SLIDE DECK OUTLINE**\n");
        sb.append("📌 **Topic:** ").append(topic.toUpperCase()).append("\n\n");

        sb.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
        sb.append("🔹 **SLIDE 1: Title & Introduction**\n");
        sb.append("• Heading: \"").append(topic).append(": Overview & Future Potential\"\n");
        sb.append("• Subtitle: Real-world Applications & Key Challenges\n");
        sb.append("• Presenter Notes: Audience ko hook karne ke liye ek strong opening stat se start karein.\n\n");

        sb.append("🔹 **SLIDE 2: The Core Problem Statement**\n");
        sb.append("• Current limitations in traditional approaches.\n");
        sb.append("• Pain points faced by users/industries.\n");
        sb.append("• Why an innovative solution is urgently needed today.\n\n");

        sb.append("🔹 **SLIDE 3: Key Architecture & Working Principle**\n");
        sb.append("• Step-by-step pipeline from input to execution.\n");
        sb.append("• Comparison: Conventional methods vs modern approaches.\n");
        sb.append("• Key technologies & frameworks involved.\n\n");

        sb.append("🔹 **SLIDE 4: Real-world Use Cases & Impact**\n");
        sb.append("• Case Study 1: High efficiency in field operations.\n");
        sb.append("• Case Study 2: Low resource footprint & scalability.\n");
        sb.append("• Measurable metrics (speed, cost reduction, reliability).\n\n");

        sb.append("🔹 **SLIDE 5: Roadmap & Conclusion**\n");
        sb.append("• Next milestones & upcoming features.\n");
        sb.append("• Summary of core takeaways.\n");
        sb.append("• Q&A session invite.\n");
        sb.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n");
        sb.append("💡 *Tip: Aap is structure ko copy karke PowerPoint ya Google Slides me seedha paste kar sakte hain!*");

        return ToolResult.text(sb.toString()).addChip("Export Summary");
    }

    private static String extractTopic(String prompt) {
        String clean = prompt.replaceAll("(?i)(bhai|pe|par|mujhe|banana|banani|hai|presentation|ppt|slides|topic)", "").trim();
        return clean.isEmpty() ? "Emerging Technologies" : clean;
    }
}
