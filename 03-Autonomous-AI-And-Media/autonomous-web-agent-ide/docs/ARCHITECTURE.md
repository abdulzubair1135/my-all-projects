# Autonomous Web-Agent IDE — Architecture & System Design

## 1. Overview

The **Autonomous Web-Agent IDE** is a local-first platform that translates natural-language software specifications into verified running applications. It pairs Playwright-driven browser automation with a strict security sandbox, policy engine, WebSocket-streamed terminal output, Monaco editor, and SQLite state persistence.

```
┌──────────────────────────────────────────────────────────────┐
│                    React IDE Frontend                        │
│    • Monaco Editor  • xterm.js Terminal  • Task Graph DAG    │
└──────────────────────────────┬───────────────────────────────┘
                               │ REST + WebSockets (/ws)
┌──────────────────────────────▼───────────────────────────────┐
│               Node.js Express Controller Backend             │
│    • SQLite State Store   • File Watcher (chokidar)          │
│    • Process Manager      • Agent Process Bridge             │
└──────────────────────────────┬───────────────────────────────┘
                               │ IPC (JSON Stream / Subprocess)
┌──────────────────────────────▼───────────────────────────────┐
│                    Python 3.11+ Agent Core                   │
│    • Planner & DAG Mgr    • Protocol Parser & Validator      │
│    • PathGuard Sandbox    • Command Policy Engine            │
│    • Error Analyzer       • Loop Detector (Anti-Spin)        │
└──────────────┬───────────────────────────────┬───────────────┘
               │                               │
               ▼                               ▼
    ┌──────────────────────┐        ┌──────────────────────┐
    │  Playwright Browser  │        │   Sandboxed Project  │
    │  (DeepSeek Web / LLM)│        │   Workspace FS & Git │
    └──────────────────────┘        └──────────────────────┘
```

---

## 2. Core Subsystems

### A. React IDE Frontend
- Built with **React 18**, **Vite**, and **Tailwind CSS**.
- **Monaco Editor**: Multi-tab code editor with syntax highlighting, line numbers, automatic language detection, and `Ctrl+S` saving.
- **xterm.js Terminal**: Streams real-time stdout and stderr ANSI logs from agent commands and background servers.
- **Task Graph Visualizer**: Displays task dependencies, execution state (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`), and retry badges.
- **Security Approval Modal**: Prompts the developer when `CAUTION` or `DANGEROUS` actions are evaluated by the policy engine.

### B. Node.js Express Controller Backend
- **REST API (`/api/*`)**: Manages project workspaces, file reading/writing with SHA256 conflict detection, processes, and agent controls (`start`, `pause`, `resume`, `stop`, `override`).
- **WebSocket Server (`/ws`)**: Broadcasts unified events (`task.*`, `command.output`, `file.*`, `process.*`, `approval.*`) with an in-memory event replay buffer.
- **File Watcher (`chokidar`)**: Observes external file edits in active workspace and synchronizes with the frontend.
- **Process Manager**: Supervises background development servers (e.g. `npm run dev`, `python server.py`), detects listening ports, and handles graceful teardown on shutdown.

### C. Python 3.11+ Agent Core
- **Planner**: Decomposes user instructions into a dependency-ordered task graph (`ProjectPlan`).
- **Protocol Parser & Validator**: Extracts and heals JSON responses from LLMs, validating them against Pydantic models.
- **PathGuard**: Enforces workspace boundary containment, neutralizing directory traversal, Windows device paths (`CON`, `NUL`), UNC paths, and symlink breakout.
- **Command Policy Engine**: Classifies commands into `SAFE`, `CAUTION`, `DANGEROUS`, and `BLOCKED` tiers using token parsing and AST analysis.
- **Error Analyzer & Loop Detector**: Categorizes runtime stack traces and generates error fingerprints to halt infinite retry loops.
- **Git Manager**: Automatically creates commits before and after tasks, enabling atomic diff inspections and rollbacks.
