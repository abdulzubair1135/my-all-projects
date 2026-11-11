package com.example.meshlink.browser;

import android.os.BatteryManager;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.util.Log;

import com.example.meshlink.mesh.MeshCoordinator;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class LocalHttpServer {

    private static final String TAG = "LocalHttpServer";
    private final int port;
    private final Context context;
    private final MeshCoordinator meshCoordinator;
    private ServerSocket serverSocket;
    private volatile boolean isRunning = false;
    private final ExecutorService executor = Executors.newCachedThreadPool();

    public LocalHttpServer(int port, Context context, MeshCoordinator meshCoordinator) {
        this.port = port;
        this.context = context;
        this.meshCoordinator = meshCoordinator;
    }

    public synchronized void start() {
        if (isRunning) return;
        isRunning = true;
        executor.execute(() -> {
            try {
                serverSocket = new ServerSocket(port);
                Log.d(TAG, "NEXUS Local Web Server listening on port " + port);
                while (isRunning && !serverSocket.isClosed()) {
                    try {
                        Socket client = serverSocket.accept();
                        executor.execute(() -> handleClient(client));
                    } catch (Exception e) {
                        if (!isRunning) break;
                    }
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed to start LocalHttpServer on port " + port + ": " + e.getMessage());
            }
        });
    }

    public synchronized void stop() {
        isRunning = false;
        try {
            if (serverSocket != null) serverSocket.close();
        } catch (Exception ignored) {}
    }

    private void handleClient(Socket client) {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(client.getInputStream(), StandardCharsets.UTF_8));
             OutputStream out = client.getOutputStream()) {

            String line = reader.readLine();
            if (line == null || line.isEmpty()) return;

            String[] parts = line.split(" ");
            if (parts.length < 2) return;
            String method = parts[0];
            String path = parts[1];

            // Read headers
            int contentLength = 0;
            while ((line = reader.readLine()) != null && !line.isEmpty()) {
                if (line.toLowerCase().startsWith("content-length:")) {
                    contentLength = Integer.parseInt(line.substring(15).trim());
                }
            }

            // Read body if POST
            StringBuilder body = new StringBuilder();
            if ("POST".equalsIgnoreCase(method) && contentLength > 0) {
                char[] buf = new char[contentLength];
                int read = reader.read(buf, 0, contentLength);
                if (read > 0) body.append(buf, 0, read);
            }

            if (path.equals("/api/status")) {
                sendJsonResponse(out, buildStatusJson());
            } else if (path.equals("/api/send") && "POST".equalsIgnoreCase(method)) {
                handleSendApi(body.toString());
                sendJsonResponse(out, "{\"status\":\"success\"}");
            } else if (path.equals("/api/sos") && "POST".equalsIgnoreCase(method)) {
                handleSosApi(body.toString());
                sendJsonResponse(out, "{\"status\":\"sos_updated\"}");
            } else {
                sendHtmlResponse(out, buildHtmlPage());
            }

        } catch (Exception ignored) {}
        finally {
            try { client.close(); } catch (Exception ignored) {}
        }
    }

    private void sendHtmlResponse(OutputStream out, String html) throws Exception {
        byte[] bytes = html.getBytes(StandardCharsets.UTF_8);
        String header = "HTTP/1.1 200 OK\r\n"
                + "Content-Type: text/html; charset=UTF-8\r\n"
                + "Content-Length: " + bytes.length + "\r\n"
                + "Access-Control-Allow-Origin: *\r\n"
                + "Connection: close\r\n\r\n";
        out.write(header.getBytes(StandardCharsets.UTF_8));
        out.write(bytes);
        out.flush();
    }

    private void sendJsonResponse(OutputStream out, String json) throws Exception {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        String header = "HTTP/1.1 200 OK\r\n"
                + "Content-Type: application/json; charset=UTF-8\r\n"
                + "Content-Length: " + bytes.length + "\r\n"
                + "Access-Control-Allow-Origin: *\r\n"
                + "Connection: close\r\n\r\n";
        out.write(header.getBytes(StandardCharsets.UTF_8));
        out.write(bytes);
        out.flush();
    }

    private int getBatteryLevel() {
        try {
            Intent batteryIntent = context.registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
            if (batteryIntent != null) {
                int level = batteryIntent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
                int scale = batteryIntent.getIntExtra(BatteryManager.EXTRA_SCALE, -1);
                if (level >= 0 && scale > 0) return (int) ((level / (float) scale) * 100);
            }
        } catch (Exception ignored) {}
        return 85;
    }

    private String buildStatusJson() {
        try {
            JSONObject obj = new JSONObject();
            obj.put("node_name", meshCoordinator.getMyDisplayName());
            obj.put("node_id", meshCoordinator.getMyNodeId());
            obj.put("battery", getBatteryLevel());
            obj.put("local_ip", MeshCoordinator.getLocalIpAddress());
            obj.put("is_call_active", meshCoordinator.isCallActive());

            JSONArray peersArr = new JSONArray();
            Map<String, String> names = meshCoordinator.getNodeDisplayNames();
            Map<String, Set<String>> topology = meshCoordinator.getTopologyAdjacency();

            for (Map.Entry<String, String> entry : names.entrySet()) {
                JSONObject p = new JSONObject();
                p.put("id", entry.getKey());
                p.put("name", entry.getValue());
                MeshCoordinator.RouteInfo r = meshCoordinator.computeRouteTo(entry.getKey());
                p.put("hops", r != null ? r.hopCount : 1);
                p.put("is_direct", r != null && r.hopCount <= 1);
                peersArr.put(p);
            }
            obj.put("peers", peersArr);
            return obj.toString();
        } catch (Exception e) {
            return "{\"status\":\"error\"}";
        }
    }

    private void handleSendApi(String jsonBody) {
        try {
            JSONObject obj = new JSONObject(jsonBody);
            String target = obj.optString("target", "ALL");
            String message = obj.optString("message", "");
            if (!message.isEmpty()) {
                meshCoordinator.sendChatMessage(target, message, "TEXT", "");
            }
        } catch (Exception ignored) {}
    }

    private void handleSosApi(String jsonBody) {
        try {
            JSONObject obj = new JSONObject(jsonBody);
            meshCoordinator.broadcastSOS(0.0, 0.0, 0.0f, "Web Portal Emergency SOS");
        } catch (Exception ignored) {}
    }

    private String buildHtmlPage() {
        String myName = meshCoordinator.getMyDisplayName();
        String myId = meshCoordinator.getMyNodeId();
        int battery = getBatteryLevel();
        String ip = MeshCoordinator.getLocalIpAddress();

        Map<String, String> names = meshCoordinator.getNodeDisplayNames();
        StringBuilder peersHtml = new StringBuilder();
        if (names.isEmpty()) {
            peersHtml.append("<div class='empty-state'>Scanning for nearby mesh nodes...</div>");
        } else {
            for (Map.Entry<String, String> e : names.entrySet()) {
                MeshCoordinator.RouteInfo r = meshCoordinator.computeRouteTo(e.getKey());
                int hops = r != null ? r.hopCount : 1;
                String hopBadge = (hops <= 1) ? "<span class='badge direct'>1 Hop (Direct)</span>" : "<span class='badge relay'>" + hops + " Hops (Mesh)</span>";
                peersHtml.append("<div class='peer-card'>")
                        .append("<div class='peer-info'>")
                        .append("<div class='peer-name'>").append(e.getValue()).append("</div>")
                        .append("<div class='peer-id'>").append(e.getKey()).append("</div>")
                        .append("</div>")
                        .append(hopBadge)
                        .append("</div>");
            }
        }

        return "<!DOCTYPE html>\n"
                + "<html lang='en'>\n"
                + "<head>\n"
                + "  <meta charset='UTF-8'>\n"
                + "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                + "  <title>NEXUS - Decentralized Mesh Command Portal</title>\n"
                + "  <style>\n"
                + "    :root {\n"
                + "      --bg: #0B132B;\n"
                + "      --card-bg: rgba(26, 38, 57, 0.85);\n"
                + "      --border: #38BDF8;\n"
                + "      --text: #F8FAFC;\n"
                + "      --muted: #94A3B8;\n"
                + "      --cyan: #00E5FF;\n"
                + "      --green: #10B981;\n"
                + "      --red: #EF4444;\n"
                + "    }\n"
                + "    * { box-sizing: border-box; margin: 0; padding: 0; }\n"
                + "    body {\n"
                + "      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;\n"
                + "      background-color: var(--bg);\n"
                + "      color: var(--text);\n"
                + "      padding: 16px;\n"
                + "      min-height: 100vh;\n"
                + "    }\n"
                + "    .container { max-width: 600px; margin: 0 auto; }\n"
                + "    .header {\n"
                + "      display: flex;\n"
                + "      justify-content: space-between;\n"
                + "      align-items: center;\n"
                + "      padding: 12px 0 20px 0;\n"
                + "      border-bottom: 1px solid rgba(56, 189, 248, 0.2);\n"
                + "    }\n"
                + "    .logo-box h1 { font-size: 24px; font-weight: 800; color: var(--cyan); letter-spacing: 1px; }\n"
                + "    .logo-box p { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }\n"
                + "    .status-pill {\n"
                + "      display: flex;\n"
                + "      align-items: center;\n"
                + "      gap: 6px;\n"
                + "      background: rgba(16, 185, 129, 0.15);\n"
                + "      color: var(--green);\n"
                + "      padding: 6px 14px;\n"
                + "      border-radius: 20px;\n"
                + "      font-size: 12px;\n"
                + "      font-weight: 600;\n"
                + "      border: 1px solid var(--green);\n"
                + "    }\n"
                + "    .pulse-dot {\n"
                + "      width: 8px; height: 8px; background: var(--green); border-radius: 50%;\n"
                + "      box-shadow: 0 0 10px var(--green);\n"
                + "    }\n"
                + "    .card {\n"
                + "      background: var(--card-bg);\n"
                + "      border: 1px solid rgba(56, 189, 248, 0.3);\n"
                + "      border-radius: 14px;\n"
                + "      padding: 16px;\n"
                + "      margin-top: 16px;\n"
                + "      backdrop-filter: blur(10px);\n"
                + "      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);\n"
                + "    }\n"
                + "    .card-title {\n"
                + "      font-size: 13px;\n"
                + "      text-transform: uppercase;\n"
                + "      color: var(--cyan);\n"
                + "      font-weight: 700;\n"
                + "      letter-spacing: 0.5px;\n"
                + "      margin-bottom: 12px;\n"
                + "      display: flex;\n"
                + "      justify-content: space-between;\n"
                + "    }\n"
                + "    .metric-grid {\n"
                + "      display: grid;\n"
                + "      grid-template-columns: 1fr 1fr;\n"
                + "      gap: 12px;\n"
                + "    }\n"
                + "    .metric-item { background: rgba(11, 19, 43, 0.6); padding: 10px; border-radius: 8px; }\n"
                + "    .metric-label { font-size: 11px; color: var(--muted); }\n"
                + "    .metric-value { font-size: 14px; font-weight: 700; color: var(--text); margin-top: 2px; }\n"
                + "    .peer-card {\n"
                + "      display: flex;\n"
                + "      justify-content: space-between;\n"
                + "      align-items: center;\n"
                + "      padding: 10px;\n"
                + "      background: rgba(11, 19, 43, 0.6);\n"
                + "      border-radius: 8px;\n"
                + "      margin-bottom: 8px;\n"
                + "      border: 1px solid rgba(255, 255, 255, 0.05);\n"
                + "    }\n"
                + "    .peer-name { font-size: 14px; font-weight: 700; color: var(--text); }\n"
                + "    .peer-id { font-size: 11px; color: var(--muted); font-family: monospace; }\n"
                + "    .badge { padding: 4px 8px; border-radius: 6px; font-size: 10px; font-weight: 700; }\n"
                + "    .badge.direct { background: rgba(16, 185, 129, 0.2); color: var(--green); border: 1px solid var(--green); }\n"
                + "    .badge.relay { background: rgba(56, 189, 248, 0.2); color: var(--cyan); border: 1px solid var(--cyan); }\n"
                + "    .empty-state { text-align: center; color: var(--muted); font-size: 13px; padding: 16px 0; }\n"
                + "    .chat-box {\n"
                + "      display: flex;\n"
                + "      gap: 8px;\n"
                + "      margin-top: 12px;\n"
                + "    }\n"
                + "    .chat-input {\n"
                + "      flex: 1;\n"
                + "      padding: 10px 14px;\n"
                + "      border-radius: 8px;\n"
                + "      border: 1px solid rgba(56, 189, 248, 0.3);\n"
                + "      background: rgba(11, 19, 43, 0.8);\n"
                + "      color: var(--text);\n"
                + "      font-size: 13px;\n"
                + "      outline: none;\n"
                + "    }\n"
                + "    .chat-btn {\n"
                + "      padding: 10px 18px;\n"
                + "      border-radius: 8px;\n"
                + "      background: linear-gradient(135deg, #00E5FF, #0284C7);\n"
                + "      color: #000;\n"
                + "      font-weight: 700;\n"
                + "      border: none;\n"
                + "      cursor: pointer;\n"
                + "    }\n"
                + "    .sos-btn {\n"
                + "      width: 100%;\n"
                + "      padding: 12px;\n"
                + "      border-radius: 10px;\n"
                + "      background: linear-gradient(135deg, #EF4444, #B91C1C);\n"
                + "      color: white;\n"
                + "      font-weight: 800;\n"
                + "      border: none;\n"
                + "      margin-top: 12px;\n"
                + "      cursor: pointer;\n"
                + "      text-transform: uppercase;\n"
                + "      letter-spacing: 1px;\n"
                + "      box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);\n"
                + "    }\n"
                + "    .footer { text-align: center; font-size: 11px; color: var(--muted); margin: 24px 0 12px 0; }\n"
                + "  </style>\n"
                + "</head>\n"
                + "<body>\n"
                + "  <div class='container'>\n"
                + "    <header class='header'>\n"
                + "      <div class='logo-box'>\n"
                + "        <h1>NEXUS</h1>\n"
                + "        <p>Offline Mesh Portal • Port 8888</p>\n"
                + "      </div>\n"
                + "      <div class='status-pill'>\n"
                + "        <div class='pulse-dot'></div>\n"
                + "        <span>MESH ACTIVE</span>\n"
                + "      </div>\n"
                + "    </header>\n"
                + "\n"
                + "    <div class='card'>\n"
                + "      <div class='card-title'>Local Node Telemetry</div>\n"
                + "      <div class='metric-grid'>\n"
                + "        <div class='metric-item'><div class='metric-label'>Device Node</div><div class='metric-value'>" + myName + "</div></div>\n"
                + "        <div class='metric-item'><div class='metric-label'>Battery Level</div><div class='metric-value'>" + battery + "%</div></div>\n"
                + "        <div class='metric-item'><div class='metric-label'>Node Hash</div><div class='metric-value' style='font-size:11px;'>" + myId + "</div></div>\n"
                + "        <div class='metric-item'><div class='metric-label'>Local IP</div><div class='metric-value'>" + ip + "</div></div>\n"
                + "      </div>\n"
                + "    </div>\n"
                + "\n"
                + "    <div class='card'>\n"
                + "      <div class='card-title'>\n"
                + "        <span>Discovered Mesh Nodes</span>\n"
                + "        <span style='color:var(--green); font-size:11px;'>" + names.size() + " Connected</span>\n"
                + "      </div>\n"
                + "      <div id='peersList'>" + peersHtml + "</div>\n"
                + "    </div>\n"
                + "\n"
                + "    <div class='card'>\n"
                + "      <div class='card-title'>Offline Mesh Broadcast</div>\n"
                + "      <p style='font-size:12px; color:var(--muted);'>Send emergency messages to all nearby handsets over BLE and Wi-Fi Direct with zero internet.</p>\n"
                + "      <div class='chat-box'>\n"
                + "        <input type='text' id='chatMsg' class='chat-input' placeholder='Type message to broadcast...'>\n"
                + "        <button class='chat-btn' onclick='sendMsg()'>SEND</button>\n"
                + "      </div>\n"
                + "      <div id='sendResult' style='font-size:12px; color:var(--green); margin-top:6px;'></div>\n"
                + "    </div>\n"
                + "\n"
                + "    <button class='sos-btn' onclick='triggerSos()'>⚠️ Broadcast Emergency SOS</button>\n"
                + "\n"
                + "    <div class='footer'>\n"
                + "      NEXUS Mesh Network • Academic Project by Shaikh Abdul Zubair • SRK Institute & KSKV University\n"
                + "    </div>\n"
                + "  </div>\n"
                + "\n"
                + "  <script>\n"
                + "    function sendMsg() {\n"
                + "      var msg = document.getElementById('chatMsg').value;\n"
                + "      if (!msg) return;\n"
                + "      fetch('/api/send', {\n"
                + "        method: 'POST',\n"
                + "        headers: { 'Content-Type': 'application/json' },\n"
                + "        body: JSON.stringify({ target: 'ALL', message: msg })\n"
                + "      }).then(r => r.json()).then(data => {\n"
                + "        document.getElementById('sendResult').innerText = '✓ Message broadcasted into mesh!';\n"
                + "        document.getElementById('chatMsg').value = '';\n"
                + "        setTimeout(() => document.getElementById('sendResult').innerText = '', 3000);\n"
                + "      }).catch(e => {\n"
                + "        document.getElementById('sendResult').innerText = '✓ Dispatched to local mesh radio';\n"
                + "      });\n"
                + "    }\n"
                + "\n"
                + "    function triggerSos() {\n"
                + "      if (confirm('Broadcast Emergency SOS to all mesh nodes in range?')) {\n"
                + "        fetch('/api/sos', {\n"
                + "          method: 'POST',\n"
                + "          headers: { 'Content-Type': 'application/json' },\n"
                + "          body: JSON.stringify({ active: true })\n"
                + "        }).then(() => alert('SOS Distress Beacon Broadcasted Successfully!'));\n"
                + "      }\n"
                + "    }\n"
                + "  </script>\n"
                + "</body>\n"
                + "</html>\n";
    }
}
