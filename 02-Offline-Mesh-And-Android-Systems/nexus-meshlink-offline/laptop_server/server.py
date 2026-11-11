#!/usr/bin/env python3
"""
MeshLink Offline Laptop Server
Host this on your laptop when connected to Mobile Hotspot or LAN.
Phones running MeshLink can access files, news, notices, and offline tools!

How to run:
    python server.py
Access from phone:
    http://<laptop-ip>:8080
"""

import os
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

PORT = 8888
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_FILES_DIR = os.path.join(SERVER_DIR, "shared_files")
os.makedirs(SHARED_FILES_DIR, exist_ok=True)

# Sample emergency file if none exists
readme_file = os.path.join(SHARED_FILES_DIR, "emergency_guide.txt")
if not os.path.exists(readme_file):
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write("=== MESHLINK OFFLINE SURVIVAL GUIDE ===\n\n"
                "1. If cellular network is down, MeshLink relays messages over BLE mesh.\n"
                "2. High quality voice/video calls use direct WiFi P2P.\n"
                "3. Laptop server acts as a local emergency library.\n")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus MeshLink Command Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0B1120; color: #F8FAFC; padding: 18px; line-height: 1.6; }
        .container { max-width: 680px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #1E293B; }
        h1 { color: #10B981; font-size: 24px; margin-bottom: 6px; font-weight: 800; }
        .pill { display: inline-block; background: #064E3B; color: #34D399; border: 1px solid #059669; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .card { background: #1E293B; border-radius: 14px; padding: 18px; margin-bottom: 16px; border: 1px solid #334155; }
        .card-download { background: linear-gradient(135deg, #064E3B 0%, #1E293B 100%); border: 2px solid #10B981; box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2); }
        .card h2 { font-size: 17px; color: #38BDF8; margin-bottom: 8px; display: flex; align-items: center; }
        .card p { color: #94A3B8; font-size: 13px; margin-bottom: 14px; line-height: 1.5; }
        .btn { display: inline-block; background: #2563EB; color: white; padding: 10px 18px; border-radius: 10px; text-decoration: none; font-size: 13px; font-weight: bold; border: none; cursor: pointer; text-align: center; }
        .btn-green { background: #10B981; color: #022C22; font-size: 15px; font-weight: 800; padding: 14px 22px; width: 100%; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35); }
        .btn-green:hover { background: #059669; }
        ul { list-style: none; }
        li { padding: 10px 0; border-bottom: 1px solid #334155; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
        li:last-child { border-bottom: none; }
        .alert-box { background: #7F1D1D30; border: 1px solid #EF4444; color: #FCA5A5; padding: 12px 14px; border-radius: 10px; margin-bottom: 16px; font-size: 13px; }
        .badge-apk { background: #047857; color: white; padding: 3px 8px; border-radius: 6px; font-size: 11px; margin-left: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 Nexus MeshLink Portal</h1>
            <div class="pill">● LAPTOP WEBSERVER LIVE &bull; PORT 8888</div>
            <p style="color: #64748B; font-size: 12px; margin-top: 6px;">Zero Internet Required &bull; WiFi Local Hub</p>
        </header>

        <!-- Main APK Download Card for Oppo / Other Android Devices -->
        <div class="card card-download">
            <h2 style="color: #34D399;">📲 Install Latest Nexus MeshLink APK <span class="badge-apk">v1.2.0</span></h2>
            <p style="color: #E2E8F0;">Direct download link for <strong>Oppo</strong> and all connected Android devices on this WiFi network. Includes offline Qwen AI &amp; P2P mesh calling.</p>
            <a href="/files/nexus-meshlink.apk" class="btn btn-green">
                ⬇️ Download APK Now (~39.7 MB)
            </a>
        </div>

        <div class="alert-box">
            🚨 <strong>OFFGRID STATUS:</strong> Mesh nodes connected over local WiFi network. Server telemetry responding at <code>/api/status</code>.
        </div>

        <div class="card">
            <h2>📁 Shared Emergency Files &amp; Manuals</h2>
            <p>Download survival guides, documents, and emergency maps directly onto your phone.</p>
            <ul>
                <li><span>📄 emergency_guide.txt</span> <a href="/files/emergency_guide.txt" class="btn" style="padding: 6px 14px;">Download</a></li>
                <li><span>📲 nexus-meshlink.apk (Latest Build)</span> <a href="/files/nexus-meshlink.apk" class="btn" style="padding: 6px 14px;">Download</a></li>
            </ul>
        </div>

        <div class="card">
            <h2>📝 Notice Board &amp; Network News</h2>
            <p>Broadcasting to all nodes connected via browser or app socket.</p>
            <div style="background: #0F172A; padding: 10px; border-radius: 8px; font-size: 13px; color: #CBD5E1; border: 1px solid #334155;">
                🟢 <strong>Laptop Hub Active:</strong> Running on port 8888. Both phones can connect simultaneously!
            </div>
        </div>
    </div>
</body>
</html>
"""

class MeshHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
        elif self.path.startswith("/files/"):
            fname = self.path[len("/files/"):]
            fpath = os.path.join(SHARED_FILES_DIR, fname)
            if os.path.exists(fpath):
                self.send_response(200)
                self.send_header("Content-type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
                self.end_headers()
                with open(fpath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File Not Found")
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = {"status": "ONLINE", "server": "MeshLink Laptop Hub", "ip": get_local_ip()}
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))

def main():
    ip = get_local_ip()
    print("=" * 60)
    print("  [+] MESHLINK OFFLINE LAPTOP SERVER STARTED")
    print("=" * 60)
    print(f"  Local IP Address : {ip}")
    print(f"  Server URL       : http://{ip}:{PORT}")
    print(f"  Hotspot IP (typ.): http://192.168.137.1:{PORT}")
    print("  Shared files dir :", SHARED_FILES_DIR)
    print("=" * 60)
    print("  Press Ctrl+C to stop the server\n")

    server = HTTPServer(("0.0.0.0", PORT), MeshHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping MeshLink Server...")
        server.server_close()

if __name__ == "__main__":
    main()
