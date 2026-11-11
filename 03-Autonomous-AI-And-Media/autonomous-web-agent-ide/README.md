# Autonomous Web-Agent IDE

> A production-grade local desktop/web application that transforms natural-language project requirements into full-stack, tested, and running code using web-based LLMs via persistent Playwright automation, strict sandboxing, policy validation, and real-time streaming.

---

## Key Highlights

- **Web-Based LLM Integration**: Communicates with web-based LLMs (e.g. DeepSeek Web) via persistent Playwright browser sessions without requiring paid API tokens.
- **Strict Security Sandbox**: `PathGuard` prevents directory traversal, symlink breakouts, Windows device name vulnerabilities, and UNC path injection.
- **Command Policy Engine**: Classifies commands into `SAFE`, `CAUTION`, `DANGEROUS`, and `BLOCKED` with interactive developer approvals.
- **Developer IDE UI**: Dark theme, Monaco editor with multi-tab editing, real-time xterm.js terminal streaming, interactive task graph DAG, and command palette (`Ctrl+P`).
- **Autonomous Error Recovery & Loop Prevention**: Captures command errors, calculates error fingerprints, and halts infinite loops after 3 repetitive attempts.
- **Managed Background Servers**: Tracks long-running dev servers (`npm run dev`), detects ports, and cleanly tears down processes on exit.
- **Automatic Git Checkpointing**: Commits progress before and after each task and repair attempt for rollbacks and diff comparisons.

---

## Project Structure

```text
autonomous-web-agent-ide/
├── frontend/             # React 18 + Vite + Tailwind + Monaco + xterm.js
├── backend/              # Node.js Express + SQLite + WebSockets + Process Manager
├── agent/                # Python 3.11+ Agent Core (Planner, Sandbox, Browser, Recovery)
├── workspace/            # Isolated project workspaces
├── data/                 # SQLite database (agent.sqlite)
├── browser-profile/      # Persistent Chromium profile for session cookies
├── docs/                 # Architecture, Security, Protocol, Troubleshooting
└── package.json          # Monorepo runner
```

---

## Quickstart

### 1. Install Dependencies
```bash
# Root & Submodules
npm install
cd backend && npm install
cd ../frontend && npm install
cd ../agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Development Servers
From the root directory:
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Running Tests

```bash
# Python Security, Sandbox & Protocol tests
cd agent && pytest -v

# Backend REST & SQLite tests
cd backend && npm test

# Frontend build verification
cd frontend && npm run build
```

---

## License
MIT
