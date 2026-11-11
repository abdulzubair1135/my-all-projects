"""
antigravity_watchdog.py
=======================
Autonomous Self-Healing Supervisor for Stickman Factory.
- Intercepts crashes, render errors, or upload failures in stickman_project.
- Automatically launches Antigravity into stickman_project.
- Dumps full traceback, error diagnostics, and resolution checklist to:
  1. Active Antigravity Conversation via Google AgentAPI (agentapi.bat send-message).
  2. ANTIGRAVITY_ERROR_REPORT.md in project root.
  3. Windows Clipboard for instant paste (Ctrl+V).
- WAITS in an intelligent loop until Antigravity fixes the code.
- Auto-detects file modifications & compiles/validates syntax before resuming.
- Once fixed, seamlessly continues the factory pipeline right where it left off!
"""

import sys
import os
import time
import json
import traceback
import subprocess
import sqlite3
import py_compile

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_DIR = r"c:\Users\abdul\source\repos\stickman\stickman_project"
ANTIGRAVITY_EXE = r"C:\Users\abdul\AppData\Local\Programs\antigravity\Antigravity.exe"
AGENTAPI_BAT = r"C:\Users\abdul\.gemini\antigravity\bin\agentapi.bat"
CONVO_DB = r"C:\Users\abdul\.gemini\antigravity\conversation_summaries.db"
FALLBACK_CONVO_ID = "a28b7e23-4a1d-490e-86cb-c5a75cf0dcb2"

LOCK_FILE = os.path.join(PROJECT_DIR, "WAITING_FOR_ANTIGRAVITY_FIX.lock")
STATUS_FILE = os.path.join(PROJECT_DIR, "incident_status.json")
REPORT_MD = os.path.join(PROJECT_DIR, "ANTIGRAVITY_ERROR_REPORT.md")


def get_active_antigravity_convo_id():
    """Dynamically finds the latest active Antigravity conversation ID for stickman_project."""
    if os.path.exists(CONVO_DB):
        try:
            con = sqlite3.connect(CONVO_DB, timeout=2)
            cur = con.cursor()
            cur.execute(
                "SELECT conversation_id FROM conversation_summaries "
                "WHERE workspace_uris LIKE '%stickman%' "
                "ORDER BY last_modified_time DESC LIMIT 1"
            )
            row = cur.fetchone()
            con.close()
            if row and row[0]:
                return row[0]
        except Exception:
            pass
    return FALLBACK_CONVO_ID


def open_antigravity_app(project_path=PROJECT_DIR):
    """Brings Antigravity Electron Desktop app to foreground in the stickman_project workspace."""
    print("[*] Opening Google Antigravity in stickman_project...", flush=True)
    if os.path.exists(ANTIGRAVITY_EXE):
        try:
            subprocess.Popen([ANTIGRAVITY_EXE, project_path])
        except Exception as e:
            print(f"[!] Could not launch Antigravity.exe directly: {e}", flush=True)

    # Bring to foreground using PowerShell
    ps_focus = """
    $wshell = New-Object -ComObject WScript.Shell
    $wshell.AppActivate('Antigravity')
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_focus], capture_output=True, timeout=5)
    except Exception:
        pass


def copy_to_clipboard(text):
    """Copies the text to Windows clipboard for easy Ctrl+V."""
    try:
        escaped = text.replace('"', '`"').replace("'", "''")
        ps = f"Set-Clipboard -Value @'\n{text}\n'@"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=5)
    except Exception:
        pass


def send_message_to_antigravity(convo_id, message_text, title="Stickman Error Alert"):
    """Dispatches a direct prompt message to the active Antigravity conversation via agentapi."""
    if not os.path.exists(AGENTAPI_BAT):
        print(f"[!] agentapi.bat not found at: {AGENTAPI_BAT}", flush=True)
        return False

    try:
        cmd = [AGENTAPI_BAT, "send-message", f"--title={title}", convo_id, message_text]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0:
            print(f"[OK] Error dispatched directly to Antigravity conversation ({convo_id[:8]}...)!", flush=True)
            return True
        else:
            print(f"[!] agentapi warning: {res.stderr.strip()}", flush=True)
    except Exception as e:
        print(f"[!] Could not send message via agentapi: {e}", flush=True)
    return False


def generate_error_report(error, topic="Unknown", context="Stickman Pipeline Execution"):
    """Generates an exhaustive diagnostic markdown report of the problem."""
    tb_str = "".join(traceback.format_exception(type(error), error, error.__traceback__)) if isinstance(error, Exception) else str(error)

    # Determine faulty file and line
    faulty_file = None
    faulty_line = None
    if isinstance(error, Exception) and error.__traceback__:
        tb = error.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        faulty_file = tb.tb_frame.f_code.co_filename
        faulty_line = tb.tb_lineno

    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    md_content = f"""# 🚨 STICKMAN FACTORY: INCIDENT REPORT

**Timestamp:** {now_str}  
**Context:** {context}  
**Active Topic:** `{topic}`  
**Faulty File:** `{faulty_file or 'Unknown'}`  
**Line Number:** `{faulty_line or 'Unknown'}`  

---

## 💥 Error Message
```text
{str(error)}
```

## 📜 Full Stack Traceback
```python
{tb_str}
```

---

## 🛠️ Instructions for Antigravity Agent
1. Inspect the faulty file: `{faulty_file or 'stickman_project'}`.
2. Resolve the bug, compile error, or network/API failure.
3. Once your code edits are saved, the Watchdog will **automatically detect the file modification**, verify syntax compilation with `py_compile`, and resume the factory queue!
4. Alternatively, you can signal resolution by running:
   ```powershell
   python antigravity_watchdog.py --resolved
   ```
   or by setting `"status": "RESOLVED"` in `incident_status.json`.
"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    return faulty_file, faulty_line, tb_str


def wait_for_fix(faulty_file=None, timeout_sec=1800):
    """
    Blocks and monitors for fix resolution.
    Resumes automatically when:
    1. Faulty file timestamp changes AND py_compile passes.
    2. LOCK_FILE is deleted.
    3. STATUS_FILE status becomes 'RESOLVED' or 'FIXED'.
    """
    initial_mtime = 0
    if faulty_file and os.path.exists(faulty_file):
        try:
            initial_mtime = os.path.getmtime(faulty_file)
        except Exception:
            pass

    # Record lock and status
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        f.write(f"WAITING_FOR_FIX\nTimestamp: {time.time()}\nFile: {faulty_file}\n")

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "status": "WAITING_FOR_FIX",
            "timestamp": time.time(),
            "faulty_file": faulty_file
        }, f, indent=2)

    print("\n" + "=" * 76)
    print("⏳ WATCHDOG WAITING FOR ANTIGRAVITY TO SOLVE THE PROBLEM...")
    print("=" * 76)
    print(f"[*] Faulty File under watch: {faulty_file or 'Project files'}")
    print("[*] Antigravity can edit the code, or run: python antigravity_watchdog.py --resolved")
    print("[*] Polling every 2.5 seconds...\n", flush=True)

    start_t = time.time()
    dots = 0

    while time.time() - start_t < timeout_sec:
        time.sleep(2.5)
        dots = (dots + 1) % 4
        print(f"\r[WAITING] Checking for fix resolution{'.' * dots}    ", end="", flush=True)

        # Condition 1: LOCK_FILE removed manually
        if not os.path.exists(LOCK_FILE):
            print("\n[OK] Lock file removed! Fix acknowledged.", flush=True)
            return True

        # Condition 2: STATUS_FILE updated to RESOLVED / FIXED
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    s_data = json.load(f)
                    if s_data.get("status", "").upper() in ["RESOLVED", "FIXED", "DONE"]:
                        print("\n[OK] incident_status.json marked as RESOLVED!", flush=True)
                        if os.path.exists(LOCK_FILE):
                            os.remove(LOCK_FILE)
                        return True
            except Exception:
                pass

        # Condition 3: Faulty file was edited and compiles cleanly
        if faulty_file and os.path.exists(faulty_file):
            try:
                cur_mtime = os.path.getmtime(faulty_file)
                if cur_mtime > initial_mtime:
                    # File was modified by Antigravity! Test compile
                    try:
                        py_compile.compile(faulty_file, doraise=True)
                        print(f"\n[SUCCESS] File '{os.path.basename(faulty_file)}' was updated by Antigravity and syntax is valid!", flush=True)
                        if os.path.exists(LOCK_FILE):
                            os.remove(LOCK_FILE)
                        with open(STATUS_FILE, "w", encoding="utf-8") as f:
                            json.dump({"status": "RESOLVED", "timestamp": time.time()}, f)
                        return True
                    except py_compile.PyCompileError as c_err:
                        print(f"\n[!] File modified but contains syntax error: {c_err}. Still waiting...", flush=True)
                        initial_mtime = cur_mtime
            except Exception:
                pass

    print("\n[!] Watchdog wait timed out (30 mins). Continuing...", flush=True)
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    return False


def report_and_wait_for_fix(error, topic="Unknown Topic", context="Pipeline Step"):
    """
    Master entrypoint to call whenever stickman encounters an issue:
    1. Opens Antigravity app.
    2. Writes diagnostic report in stickman_project.
    3. Dispatches prompt directly to Antigravity conversation.
    4. Waits until Antigravity solves it.
    5. Returns True to resume.
    """
    print("\n" + "!" * 76)
    print("🚨 [STICKMAN WATCHDOG] ERROR ENCOUNTERED! ACTIVATING ANTIGRAVITY FIX ENGINE")
    print("!" * 76)

    # 1. Generate full error report
    faulty_file, faulty_line, tb_str = generate_error_report(error, topic=topic, context=context)

    # 2. Open Antigravity in stickman_project
    open_antigravity_app(PROJECT_DIR)

    # 3. Find active conversation ID
    convo_id = get_active_antigravity_convo_id()

    # 4. Craft high-priority message for Antigravity
    prompt_msg = (
        f"🚨 STICKMAN PIPELINE ERROR ALERT!\n"
        f"Topic: '{topic}'\n"
        f"Context: {context}\n"
        f"Error: {str(error)}\n"
        f"File: {faulty_file} (Line {faulty_line})\n\n"
        f"A full diagnostic report has been saved to 'ANTIGRAVITY_ERROR_REPORT.md'.\n"
        f"Please analyze the traceback, fix the code in stickman_project, and signal resolution so the factory can continue!"
    )

    # 5. Dispatch message to Antigravity
    send_message_to_antigravity(convo_id, prompt_msg, title=f"Stickman Error: {str(error)[:40]}")

    # 6. Copy to clipboard for easy Ctrl+V fallback
    copy_to_clipboard(prompt_msg)

    # 7. Audible Windows beep alert
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", "[console]::beep(800, 350)"], capture_output=True, timeout=2)
    except Exception:
        pass

    # 8. Wait for Antigravity to solve the issue
    return wait_for_fix(faulty_file=faulty_file)


def run_supervised_factory():
    """
    Runs auto_factory_batch.py under active watchdog supervision.
    If it crashes or hits an unhandled error, triggers Antigravity fix flow and restarts.
    """
    print("=" * 80)
    print("       STICKMAN FACTORY: ANTIGRAVITY SUPERVISED WATCHDOG ACTIVE")
    print("=" * 80)

    while True:
        cmd = [sys.executable, "auto_factory_batch.py"]
        proc = subprocess.Popen(cmd)
        ret_code = proc.wait()

        if ret_code == 0:
            print("\n[DONE] Factory batch finished cleanly.")
            break
        else:
            print(f"\n[!] Factory exited with error code {ret_code}.")
            # Read last lines of output or report crash
            report_and_wait_for_fix(
                error=RuntimeError(f"auto_factory_batch.py crashed with exit code {ret_code}"),
                topic="Active Queue Topic",
                context="Supervised Factory Process"
            )
            print("[*] Restarting factory batch post-fix...\n")
            time.sleep(3)


if __name__ == "__main__":
    if "--resolved" in sys.argv or "--done" in sys.argv:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"status": "RESOLVED", "timestamp": time.time()}, f)
        print("[SUCCESS] Stickman incident marked as RESOLVED! Pipeline resuming.")
        sys.exit(0)

    elif "--test-alert" in sys.argv:
        print("[*] Running simulated error alert...")
        try:
            raise ValueError("SIMULATED TEST ERROR: DeepSeek timeout simulation for Watchdog")
        except Exception as e:
            report_and_wait_for_fix(e, topic="Simulated Watchdog Test Topic", context="Test Alert Command")
        sys.exit(0)

    else:
        run_supervised_factory()
