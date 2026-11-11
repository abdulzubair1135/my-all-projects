"""
AURA Local Web Dashboard (FastAPI).
Serves real-time system metrics, memory visualization, and control actions on http://localhost:8000.
"""

import os
from typing import Dict, Any
from core.controller import controller
from core.agent import agent
from database.db import db_manager
from evolution.self_evaluation import self_evaluation_engine
from memory.self_model import self_model
from config import config

# Optional FastAPI import for web server
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    import uvicorn

    app = FastAPI(title="AURA Dashboard", description="Autonomous Local AI System Dashboard")

    @app.get("/api/status")
    def get_status() -> Dict[str, Any]:
        metrics = self_evaluation_engine.evaluate_system_performance()
        summary = self_model.get_self_summary()
        return {
            "status": agent.state.value,
            "autonomy_level": controller.autonomy_level,
            "is_paused": controller.is_paused,
            "is_stopped": controller.is_stopped,
            "metrics": metrics,
            "known_topics": summary["known_topics"],
            "knowledge_gaps": summary["knowledge_gaps"],
            "available_tools": summary["available_tools"],
            "practiced_skills": summary["practiced_skills"]
        }

    @app.post("/api/control/pause")
    def pause_agent() -> Dict[str, str]:
        controller.pause()
        return {"status": "paused"}

    @app.post("/api/control/resume")
    def resume_agent() -> Dict[str, str]:
        controller.resume()
        return {"status": "resumed"}

    @app.post("/api/control/stop")
    def stop_agent() -> Dict[str, str]:
        controller.stop()
        return {"status": "stopped"}

    @app.post("/api/control/autonomy")
    def set_autonomy(level: int) -> Dict[str, Any]:
        controller.autonomy_level = max(0, min(4, level))
        return {"status": "success", "autonomy_level": controller.autonomy_level}

    @app.get("/", response_class=HTMLResponse)
    def render_dashboard():
        return """<!DOCTYPE html>
<html>
<head>
    <title>AURA Autonomous System Dashboard</title>
    <meta charset="utf-8">
    <style>
        body { font-family: monospace; background: #0f172a; color: #f8fafc; margin: 20px; }
        h1 { color: #38bdf8; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: #1e293b; padding: 15px; border-radius: 8px; border: 1fr solid #334155; }
        .btn { padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 10px; }
        .btn-pause { background: #f59e0b; color: white; }
        .btn-resume { background: #10b981; color: white; }
        .btn-stop { background: #ef4444; color: white; }
        pre { background: #020617; padding: 10px; border-radius: 4px; overflow-x: auto; color: #a7f3d0; }
    </style>
</head>
<body>
    <h1>AURA — Autonomous Local AI System</h1>
    <div class="card">
        <h3>System Controls</h3>
        <button class="btn btn-pause" onclick="fetch('/api/control/pause', {method:'POST'})">PAUSE</button>
        <button class="btn btn-resume" onclick="fetch('/api/control/resume', {method:'POST'})">RESUME</button>
        <button class="btn btn-stop" onclick="fetch('/api/control/stop', {method:'POST'})">EMERGENCY STOP</button>
    </div>
    <br>
    <div class="grid">
        <div class="card">
            <h3>Live Telemetry & Status</h3>
            <div id="status-display">Loading telemetry...</div>
        </div>
        <div class="card">
            <h3>Cognitive Memory & Knowledge Gaps</h3>
            <div id="memory-display">Loading memory state...</div>
        </div>
    </div>

    <script>
        async function updateDashboard() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('status-display').innerHTML = '<pre>' + JSON.stringify({
                    status: data.status,
                    autonomy_level: data.autonomy_level,
                    is_paused: data.is_paused,
                    is_stopped: data.is_stopped,
                    metrics: data.metrics
                }, null, 2) + '</pre>';
                document.getElementById('memory-display').innerHTML = '<pre>' + JSON.stringify({
                    known_topics: data.known_topics,
                    knowledge_gaps: data.knowledge_gaps,
                    practiced_skills: data.practiced_skills,
                    available_tools: data.available_tools
                }, null, 2) + '</pre>';
            } catch(e) { console.error(e); }
        }
        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>"""

    def run_dashboard(host: str = "127.0.0.1", port: int = 8000):
        uvicorn.run(app, host=host, port=port)

except ImportError:
    app = None
    def run_dashboard(*args, **kwargs):
        print("FastAPI or uvicorn not installed. Dashboard disabled.")
