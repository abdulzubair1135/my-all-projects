# PocketAI Bridge - Installation & Setup Guide

**PocketAI Bridge** turns your Android phone running the **Nexus** offline AI app into a portable, high-performance local AI server powered by the on-device **Qwen3 (1.7B / 0.6B) LLM** and **native llama.cpp**. Your Windows laptop communicates with the phone through local Wi-Fi / Hotspot with **zero internet connection required**.

---

## Architecture Overview

```
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│     Windows 10/11 Laptop        │                 │        AI Nova 5G Phone         │
│  (Connected to Phone Hotspot)   │                 │      (Hotspot ON, Data OFF)     │
│                                 │                 │                                 │
│  python ask.py test.txt         │  HTTP Port 8800 │  PocketAI Server (Android Svc)  │
│  - Reads test.txt questions     ├────────────────►│  - Multi-threaded HTTP Dispatch │
│  - Sends sequential requests    │                 │  - Sequential Inference Queue   │
│  - Formats answer.txt           │◄────────────────┤  - llama.cpp (127.0.0.1:8080)   │
│  - Copies to Windows Clipboard  │  JSON Response  │  - Qwen3 1.7B GGUF Model        │
└─────────────────────────────────┘                 └─────────────────────────────────┘
```

---

## Step 1: Install Updated Nexus App on Phone

1. Transfer `nexus-pocketai-server.apk` located in the `PocketAI/` folder to your phone (or install via ADB):
   ```cmd
   adb install -r nexus-pocketai-server.apk
   ```
2. Open **Nexus** on your phone.
3. Navigate to the **AI tab** (5th tab in bottom navigation).
4. Tap the **PocketAI Server** icon (🌐 top header, next to settings gear) or go to **Nexus AI Settings → Open Server Dashboard**.
5. Tap **Start Server**.
   - A persistent foreground notification will appear: `"PocketAI Server Active: Running at http://<IP>:8800"`.
   - The status badge will turn **ACTIVE (Green)**.
   - Note the IP address displayed on the screen (e.g., `192.168.43.1` or `10.33.140.79`).

---

## Step 2: Set Up Phone Hotspot (100% Offline)

1. On your phone:
   - Turn **OFF Mobile Data**.
   - Turn **ON Personal Hotspot**.
2. On your Windows Laptop:
   - Connect Wi-Fi to your phone's Hotspot network.
   - Internet status may say *"No Internet, secured"* — **this is expected and 100% correct**.

---

## Step 3: Configure Windows Laptop Client

1. Open Windows Command Prompt (`cmd.exe`) or PowerShell.
2. Navigate to the `PocketAI` directory:
   ```cmd
   cd c:\Users\abdul\OneDrive\Documents\Cheater\PocketAI
   ```
3. Install required Python packages:
   ```cmd
   pip install -r requirements.txt
   ```
4. Verify or update `config.json` with your phone's IP address:
   ```json
   {
     "server_url": "http://192.168.43.1:8800",
     "auth_token": "",
     "timeout_seconds": 300,
     "max_retries": 3,
     "retry_delay_seconds": 2,
     "temperature": 0.6,
     "max_tokens": 2048,
     "output_file": "answer.txt",
     "copy_to_clipboard": true,
     "include_thought_in_answer": false
   }
   ```
   *(Note: `ask.py` also auto-detects and scans candidate IPs `192.168.43.1`, `10.33.140.79`, and `127.0.0.1` automatically).*

---

## Step 4: Run Questions from Command Line

Place your questions into `test.txt` (separated by blank lines):

```text
Explain DBMS.

What is Primary Key?

Explain Foreign Key with an example.

What is Normalization?
```

Execute the single command:

```cmd
python ask.py test.txt
```

### Expected Output:

```
========================================
POCKETAI BRIDGE
===============

[+] Connecting to phone...
[+] Checking API...
[+] Phone connected.
[+] Qwen3 1.7B Q4_K_M loaded.

[1/4] Processing question...
[+] Answer received.

[2/4] Processing question...
[+] Answer received.

[3/4] Processing question...
[+] Answer received.

[4/4] Processing question...
[+] Answer received.

========================================
[✓] ALL QUESTIONS COMPLETED
[✓] answer.txt CREATED
[✓] CLIPBOARD COPIED
====================
```

All answers are:
1. Written into `answer.txt` with full formatting, code blocks, and timestamps.
2. Automatically copied to your Windows clipboard (press `Ctrl + V` to paste anywhere!).
3. Detailed execution latency and char counts logged into `logs/history.log`.
