# StickForge AI — Troubleshooting Guide

Common issues and resolution steps for StickForge AI.

---

## 1. Browser & DeepSeek Connection

### Issue: Browser does not open when clicking "Connect DeepSeek"
* **Diagnosis**: Verify Playwright Chromium installation.
* **Resolution**:
  1. Open command prompt in project root.
  2. Run `playwright install chromium`.
  3. Check permissions on `browser/user_data/` directory.

### Issue: "Chat input element not found in DeepSeek interface" or "CloudFront 403 block"
* **Diagnosis**: DeepSeek is showing a CloudFront/Cloudflare challenge (403 block), or the user has not logged into DeepSeek in the dedicated Chromium window yet.
* **Resolution**:
  1. In **Story Studio**, click **`🌐 Open / Connect Browser`** to launch the visible Chromium browser.
  2. If a CloudFront 403, Cloudflare challenge, or Login page appears, complete the login or verification challenge in the browser window.
  3. Once logged in, click **`🔍 Check Session`** to confirm readiness.
  4. Alternatively, switch **AI Engine** in the top bar to **`Local Offline AI (Instant & Reliable)`** to generate stories immediately without needing external web access!

### Issue: "Continue" button clicked multiple times or text repeated
* **Diagnosis**: Page state detector triggered prematurely before DeepSeek completed generation.
* **Resolution**:
  1. StickForge AI includes a built-in debounce and state-lock timer in `LongResponseManager`.
  2. Ensure the network connection is stable; check `logs/browser.log` for state transition events.

---

## 2. Rendering & FFmpeg

### Issue: "FFmpeg not found" error during video export
* **Diagnosis**: FFmpeg binary is missing from system PATH.
* **Resolution**:
  1. StickForge AI checks system PATH as well as local Python Scripts paths.
  2. Ensure `ffmpeg.exe` exists in PATH or `C:\Users\<user>\AppData\Local\Programs\Python\Python310\Scripts\ffmpeg.exe`.
  3. Run `launch_setup.bat` to re-run automated verification.

### Issue: Render job hangs or uses excessive memory
* **Diagnosis**: High-resolution rendering running on limited RAM.
* **Resolution**:
  1. In Settings, toggle preview render mode or lower export framerate from 60 FPS to 30 FPS.
  2. The frame compositor streams frames to FFmpeg through pipes rather than accumulating all frames in RAM.

---

## 3. Voice & Audio

### Issue: Edge TTS fails with network timeout
* **Diagnosis**: Internet connection interrupted or Microsoft Edge TTS endpoint throttled.
* **Resolution**:
  1. Switch TTS provider to `Offline pyttsx3` in Settings or Voice Studio.
  2. Retry failed audio segment specifically using the "Regenerate Segment" button.

---

## 4. Diagnostics Bundle
If an issue persists:
1. Open the **Diagnostics** tab in the desktop application.
2. Click **Export Diagnostics Bundle**.
3. All sensitive tokens, cookies, and local paths will be automatically redacted.
