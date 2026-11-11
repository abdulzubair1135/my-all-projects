package com.example.nearmeshchat;

import fi.iki.elonen.NanoHTTPD;

public class LocalWebServer extends NanoHTTPD {

    private final String ownerNodeId;

    public LocalWebServer(int port, String ownerNodeId) {
        super(port);
        this.ownerNodeId = ownerNodeId;
    }

    @Override
    public Response serve(IHTTPSession session) {
        String htmlContent = "<!DOCTYPE html>"
                + "<html>"
                + "<head>"
                + "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
                + "<title>Abdul Dream Mesh Node</title>"
                + "<style>"
                + "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; "
                + "       background-color: #0d1117; color: #c9d1d9; padding: 24px; text-align: center; }"
                + ".card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin: 20px auto; max-width: 480px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }"
                + "h1 { color: #58a6ff; font-size: 24px; margin-bottom: 8px; }"
                + ".tag { display: inline-block; background: #238636; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 16px; }"
                + "p { font-size: 14px; line-height: 1.6; color: #8b949e; }"
                + ".node-badge { background: #21262d; border: 1px dashed #8b949e; padding: 10px; border-radius: 8px; font-family: monospace; color: #f0883e; margin: 16px 0; }"
                + ".footer { margin-top: 24px; font-size: 12px; color: #484f58; }"
                + "</style>"
                + "</head>"
                + "<body>"
                + "<div class='card'>"
                + "<span class='tag'>OFFLINE CAPTIVE PORTAL</span>"
                + "<h1>www.abdul.dream</h1>"
                + "<p>Welcome to the decentralised offline mesh environment. You are directly communicating with a live local node without active internet.</p>"
                + "<div class='node-badge'>Host Node ID: " + ownerNodeId + "</div>"
                + "<p>Status: <strong>Mesh Gateway Active</strong></p>"
                + "</div>"
                + "<div class='footer'>Powered by NearMesh Engine</div>"
                + "</body>"
                + "</html>";

        return newFixedLengthResponse(Response.Status.OK, "text/html", htmlContent);
    }
}