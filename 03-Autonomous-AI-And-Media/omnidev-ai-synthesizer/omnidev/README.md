# 🤖 OmniDev AI

**OmniDev AI** is an autonomous, self-healing AI development agent that controls your local Chrome browser (with persistent DeepSeek & Gemini login), operates Windows Terminal / PowerShell, inspects existing codebases, builds full-stack CRUD apps, executes automated tests, and auto-corrects runtime errors.

---

## ⚡ Quick Start (Double-Click Launchers)

### 1. One-Time Chrome Setup
Double-click **`setup_login.bat`**:
- Chrome will open with port `9222` and a persistent profile folder (`chrome_profile/`).
- Log into **DeepSeek** (`chat.deepseek.com`) and/or **Gemini** (`gemini.google.com`).
- Once logged in, your session is permanently saved. You will **never** have to log in again!

### 2. Install Dependencies
Double-click **`install.bat`**:
- Automatically sets up a virtual environment and installs all dependencies and Playwright Chromium.

### 3. Launch OmniDev AI
Double-click **`run_ai.bat`**:
- Starts the interactive terminal assistant with full autonomous capabilities.

---

## 🛠️ What You Can Ask OmniDev AI To Do

### 1. Build a Full-Stack CRUD Application
```bash
build app Task Manager with priorities, due dates, and status toggle
```
- Designs SQLite schema & FastAPI backend routes.
- Writes modern Tailwind CSS responsive frontend.
- Allocates an open port and launches the server.
- Executes automated HTTP integration tests (`POST`, `GET`, `PUT`, `DELETE`).
- Auto-heals any errors or traceback issues.
- Displays live URL (e.g. `http://localhost:8000`).

### 2. Build a Modern Website / Landing Page
```bash
build website Modern landing page for an AI robotics startup with dark mode
```
- Generates complete responsive HTML5 + Tailwind CSS + interactive JS.
- Launches a local preview server on `http://localhost:8080`.

### 3. Generate a PowerPoint Presentation (.pptx)
```bash
build ppt Introduction to Quantum Computing 6 slides
```
- Creates professional widescreen slides with formatted typography, bullet points, and modern color themes.
- Saves directly to `outputs/`.

### 4. Generate AI Images
```bash
build img Futuristic cyberpunk laboratory with neon blue holograms 8k
```
- Generates high-resolution images via AI image engine and saves them to `outputs/images/`.

### 5. Modify Existing Codebases (In-Place Edits)
```bash
modify add an export to CSV button in the items table
```
- Inspects existing files, routes, classes, and imports.
- Applies precision diffs without breaking existing code.

### 6. Terminal Execution & Auto-Debugging
```bash
run python app.py
```
- Executes commands safely.
- If a command fails or crashes, OmniDev automatically captures the traceback, consults DeepSeek, applies the patch, and re-executes!
