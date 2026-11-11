# Local Development & Testing Guide

## 1. System Requirements
- **Node.js**: v20.x or higher
- **Python**: v3.11 or higher
- **Git**: Installed and available in PATH
- **OS**: Windows, macOS, or Linux

---

## 2. Setup Instructions

### Root & Node Dependencies
```bash
# Install root orchestration tools
npm install

# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install
```

### Python Agent Setup
```bash
cd ../agent

# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activate on Linux / macOS
# source .venv/bin/activate

# Install requirements & Playwright browsers
pip install -r requirements.txt
playwright install chromium
```

---

## 3. Running the Test Suite

### Run All Python Security & Protocol Tests
```bash
cd agent
pytest -v
```

### Run Backend Controller Tests
```bash
cd backend
npm test
```

### Run Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 4. Launching the IDE
From the root directory:
```bash
npm run dev
```
- **Frontend IDE**: `http://localhost:5173`
- **Backend API & WebSocket**: `http://localhost:3001`
