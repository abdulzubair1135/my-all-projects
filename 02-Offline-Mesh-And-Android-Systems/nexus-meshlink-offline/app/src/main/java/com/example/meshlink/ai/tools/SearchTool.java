package com.example.meshlink.ai.tools;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;

import org.json.JSONArray;
import org.json.JSONObject;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class SearchTool {

    private final Context context;
    private final OkHttpClient httpClient;

    public SearchTool(Context context) {
        this.context = context.getApplicationContext();
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(6, TimeUnit.SECONDS)
                .readTimeout(8, TimeUnit.SECONDS)
                .build();
    }

    public boolean isOnline() {
        try {
            ConnectivityManager cm = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
            if (cm != null) {
                NetworkInfo net = cm.getActiveNetworkInfo();
                return net != null && net.isConnected();
            }
        } catch (Exception ignored) {}
        return false;
    }

    public ToolResult search(String query) {
        if (!isOnline()) {
            return ToolResult.text(
                    "🌐 **Internet Unavailable**: Abhi device offline mode me hai.\n" +
                    "Main apne local knowledge base se answer de sakta hoon, par live web search ke liye active internet connection chahiye."
            );
        }

        // Clean query terms (e.g., "tell about bjp" -> "bjp", "who is elon musk" -> "elon musk")
        String cleanQuery = query.replaceAll("(?i)\\b(tell me about|tell about|who is|what is|kya hai|ke baare me batao|search|find|explain)\\b", "").trim();
        if (cleanQuery.isEmpty()) cleanQuery = query;

        try {
            // 1. Try Wikipedia Search API to find best matching article title
            String searchUrl = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" +
                    URLEncoder.encode(cleanQuery, StandardCharsets.UTF_8.name()) +
                    "&format=json&utf8=&srlimit=1";

            Request searchReq = new Request.Builder()
                    .url(searchUrl)
                    .header("User-Agent", "NexusMeshLink/1.0 (Android; OfflineMesh)")
                    .build();

            String pageTitle = null;
            try (Response resp = httpClient.newCall(searchReq).execute()) {
                if (resp.isSuccessful() && resp.body() != null) {
                    JSONObject json = new JSONObject(resp.body().string());
                    JSONObject queryObj = json.optJSONObject("query");
                    if (queryObj != null) {
                        JSONArray searchArr = queryObj.optJSONArray("search");
                        if (searchArr != null && searchArr.length() > 0) {
                            JSONObject firstHit = searchArr.getJSONObject(0);
                            pageTitle = firstHit.optString("title", null);
                        }
                    }
                }
            }

            if (pageTitle == null || pageTitle.isEmpty()) {
                pageTitle = cleanQuery;
            }

            // 2. Fetch full article summary for the title
            String summaryUrl = "https://en.wikipedia.org/api/rest_v1/page/summary/" +
                    URLEncoder.encode(pageTitle.replace(" ", "_"), StandardCharsets.UTF_8.name());

            Request summaryReq = new Request.Builder()
                    .url(summaryUrl)
                    .header("User-Agent", "NexusMeshLink/1.0 (Android; OfflineMesh)")
                    .build();

            try (Response resp = httpClient.newCall(summaryReq).execute()) {
                if (resp.isSuccessful() && resp.body() != null) {
                    JSONObject summaryJson = new JSONObject(resp.body().string());
                    String title = summaryJson.optString("title", pageTitle);
                    String extract = summaryJson.optString("extract", "");
                    String desc = summaryJson.optString("description", "");

                    if (!extract.isEmpty()) {
                        StringBuilder sb = new StringBuilder();
                        sb.append("🌐 **Live Information: ").append(title).append("**\n");
                        if (!desc.isEmpty()) {
                            sb.append("*(").append(desc).append(")*\n\n");
                        } else {
                            sb.append("\n");
                        }
                        sb.append(extract).append("\n\n");

                        JSONObject contentUrls = summaryJson.optJSONObject("content_urls");
                        if (contentUrls != null && contentUrls.has("desktop")) {
                            JSONObject desktop = contentUrls.optJSONObject("desktop");
                            if (desktop != null && desktop.has("page")) {
                                sb.append("🔗 Source: ").append(desktop.getString("page")).append("\n");
                            }
                        }
                        sb.append("*(Fetched via Nexus Online Search Tool)*");
                        return ToolResult.text(sb.toString()).addChip("💡 Explain More").addChip("📊 PPT Outline");
                    }
                }
            }

            // 3. Fallback to DuckDuckGo Instant Answer if Wikipedia had no extract
            String ddgUrl = "https://api.duckduckgo.com/?q=" + URLEncoder.encode(cleanQuery, StandardCharsets.UTF_8.name()) + "&format=json&no_html=1&skip_disambig=1";
            Request ddgReq = new Request.Builder().url(ddgUrl).header("User-Agent", "NexusMeshLink/1.0").build();
            try (Response resp = httpClient.newCall(ddgReq).execute()) {
                if (resp.isSuccessful() && resp.body() != null) {
                    JSONObject ddgJson = new JSONObject(resp.body().string());
                    String abstractText = ddgJson.optString("AbstractText", "");
                    if (!abstractText.isEmpty()) {
                        return ToolResult.text("🔎 **Web Summary for '" + query + "':**\n\n" + abstractText);
                    }
                }
            }

        } catch (Exception e) {
            // Network fallback
        }

        return null;
    }
}
