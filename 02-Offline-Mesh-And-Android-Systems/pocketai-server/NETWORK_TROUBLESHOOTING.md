# PocketAI Bridge - Network Troubleshooting Guide

This guide resolves network connectivity issues between your Windows laptop and your Android phone when running 100% offline.

---

## 1. Verifying Network Connection

### A. Identify Phone Gateway IP from Windows
When connected to your phone's Wi-Fi hotspot, run in Windows Command Prompt:

```cmd
ipconfig
```

Look for the Wireless LAN adapter connection:
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.43.25
   Default Gateway . . . . . . . . . : 192.168.43.1
```
The **Default Gateway** is the phone's IP address (`192.168.43.1`).

### B. Ping the Phone
```cmd
ping 192.168.43.1
```
If you get `Reply from 192.168.43.1: bytes=32 time=3ms`, the local Wi-Fi route is active.

---

## 2. Testing HTTP Endpoints Directly

You can test if the PocketAI server is listening on port 8800 using `curl` or browser on Windows:

```cmd
curl http://192.168.43.1:8800/health
```

Expected JSON response:
```json
{
  "status": "ok",
  "server": "PocketAI Server",
  "version": "1.0.0",
  "model_loaded": true,
  "model_name": "Qwen3 1.7B Q4_K_M",
  "runtime_status": "ready"
}
```

---

## 3. Resolving Android Hotspot Client Isolation

Some Android vendor builds (e.g., Transsion, Xiaomi, Realme) enable Client Isolation or strict firewall rules between the hotspot interface and local ports.

If `ping` works but `curl` times out:

1. **Check Hotspot Settings on Phone**:
   - Go to `Settings → Network & Internet → Hotspot & Tethering → Wi-Fi Hotspot`.
   - Ensure **Turn off hotspot automatically** is disabled.
   - Set AP Band to **2.4 GHz & 5 GHz (Dual band)** or **2.4 GHz** for broad compatibility.
2. **Alternative: USB Tethering (Zero Wi-Fi Interference)**:
   - Connect phone to laptop using USB-C cable.
   - Go to `Settings → Hotspot & Tethering → USB Tethering: ON`.
   - On the phone's PocketAI dashboard, the USB interface IP will appear (e.g. `10.33.140.79`).
   - Run:
     ```cmd
     python ask.py test.txt --server http://10.33.140.79:8800
     ```
   - USB tethering provides ultra-fast transfer speeds (~1ms ping) and bypasses all Wi-Fi isolation rules.

---

## 4. Windows Firewall Configuration

If Windows prevents incoming or outgoing socket connections on local networks:

1. Open Windows PowerShell as Administrator.
2. Allow outbound traffic for Python:
   ```powershell
   New-NetFirewallRule -DisplayName "PocketAI Bridge Python Outbound" -Direction Outbound -Program (Get-Command python).Source -Action Allow
   ```
3. Set your phone hotspot network profile to **Private**:
   - Go to Windows Settings → Network & Internet → Wi-Fi → Click your Phone's Wi-Fi network.
   - Select **Private network** (allows local device discovery).

---

## 5. Handling Phone Battery Optimization & Background Execution

Android 14/15 puts background apps into doze mode if unoptimized:

1. In the Nexus app, tap **Start Server**. The app runs a persistent **Foreground Service** with high-performance `WifiLock` and partial `WakeLock` during active inference.
2. Ensure battery optimization is disabled for Nexus:
   - Long press **Nexus** icon on phone launcher → **App Info (i)**.
   - Tap **Battery** or **App battery usage**.
   - Select **Unrestricted** (prevents Android from killing the server process when screen turns off).
