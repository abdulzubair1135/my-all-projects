# Troubleshooting & Recovery

## 1. Playwright Browser Login & Captcha

### Problem: `AGENT PAUSED: Manual action required`
- **Cause**: The web LLM provider requires a manual login, 2FA code, or Cloudflare/hCaptcha challenge.
- **Resolution**:
  1. Open the visible Chromium browser window spawned by the agent.
  2. Complete the login or captcha verification manually.
  3. Once logged in and on the chat interface, click **RESUME** in the Web IDE. The session cookies will be saved in `browser-profile/` for subsequent runs.

---

## 2. Port Already in Use (`EADDRINUSE`)

### Problem: Background server fails with `address already in use`
- **Resolution**:
  1. Navigate to the **Servers** tab in the IDE sidebar.
  2. Click **Stop** on the stale process.
  3. The agent error analyzer will detect the port conflict and automatically suggest an alternative port.

---

## 3. Infinite Error Loop Detected

### Problem: `[Loop Detector] Halting infinite error loop on command: ...`
- **Cause**: The agent attempted to resolve the same failing command 3 times with identical error signatures.
- **Resolution**:
  1. The agent pauses to prevent resource waste.
  2. Use the **Agent Prompt Bar** to type an explicit override instruction (e.g. `"Use sqlite3 instead of better-sqlite3"`).
  3. Click **OVERRIDE** or **RESUME**.
