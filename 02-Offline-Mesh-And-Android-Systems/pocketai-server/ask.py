#!/usr/bin/env python3
"""
POCKETAI BRIDGE - Windows Client
Connects to Nexus Android offline AI server and executes sequential Qwen3 LLM inference.
"""

import sys
import os
import json
import time
import argparse
import re
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows CMD to prevent charmap/cp1252 encoding crashes
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import requests
except ImportError:
    print("[!] Error: 'requests' package not installed. Run: pip install requests")
    sys.exit(1)

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

# Resolve directories
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
LOGS_DIR = SCRIPT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
HISTORY_LOG = LOGS_DIR / "history.log"


def load_config():
    """Loads configuration with resilient fallback defaults."""
    default_config = {
        "server_url": "http://192.168.43.1:8800",
        "auth_token": "",
        "timeout_seconds": 300,
        "max_retries": 3,
        "retry_delay_seconds": 2,
        "temperature": 0.6,
        "max_tokens": 2048,
        "output_file": "answer.txt",
        "copy_to_clipboard": True,
        "include_thought_in_answer": False
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default_config.update(loaded)
        except Exception as e:
            log_history(f"WARNING: Failed to parse config.json: {e}")
    return default_config


def log_history(message: str):
    """Appends timestamped event to history.log."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{now_str}] {message}\n"
    try:
        with open(HISTORY_LOG, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass


def extract_questions(file_path: Path) -> list[str]:
    """
    Parses questions from input text file.
    Supports separation by:
    - Multiple blank lines
    - Numbered items (1., 2., Q1:, etc.)
    - Single non-empty lines
    """
    if not file_path.exists():
        print(f"[!] Error: File '{file_path}' does not exist.")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        print(f"[!] Error: File '{file_path}' is empty.")
        sys.exit(1)

    # First attempt: split by double or more newlines
    blocks = re.split(r"\n\s*\n+", content)
    questions = []

    for block in blocks:
        trimmed = block.strip()
        if not trimmed:
            continue
        # Check if block contains multiple numbered questions
        numbered_subs = re.split(r"(?m)^\s*(?:(?:Q\s*)?\d+[\.\)\:]\s+)", trimmed)
        if len(numbered_subs) > 2:
            for sub in numbered_subs:
                s = sub.strip()
                if s:
                    questions.append(s)
        else:
            # Strip single leading numbering if present
            cleaned = re.sub(r"^\s*(?:(?:Q\s*)?\d+[\.\)\:]\s+)", "", trimmed)
            questions.append(cleaned)

    # Fallback to line by line if only one block was detected but multiple lines exist
    if len(questions) <= 1 and "\n" in content:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if len(lines) > 1:
            questions = [re.sub(r"^\s*(?:(?:Q\s*)?\d+[\.\)\:]\s+)", "", l) for l in lines]

    return [q for q in questions if q]


def discover_server(configured_url: str, auth_token: str) -> str:
    """
    Tests configured URL, and if unreachable, tests common Android hotspot/tethering IPs.
    Returns the verified working base URL or raises ConnectionError.
    """
    headers = {}
    if auth_token:
        headers["X-PocketAI-Token"] = auth_token

    candidate_urls = [configured_url]
    # Standard Android Hotspot and USB Tethering IPs
    fallback_ips = [
        "http://192.168.43.1:8800",
        "http://10.33.140.79:8800",
        "http://127.0.0.1:8800"
    ]
    for ip in fallback_ips:
        if ip not in candidate_urls:
            candidate_urls.append(ip)

    for url in candidate_urls:
        health_url = f"{url.rstrip('/')}/health"
        try:
            resp = requests.get(health_url, headers=headers, timeout=3)
            if resp.status_code == 200:
                return url.rstrip('/')
        except Exception:
            continue

    raise ConnectionError(f"Could not connect to PocketAI server on phone at {configured_url}.")


def check_and_wait_for_model(server_url: str, auth_token: str, max_wait_sec: int = 40) -> tuple[bool, str]:
    """
    Checks /health endpoint. If model is still initializing in RAM, polls until ready.
    """
    headers = {}
    if auth_token:
        headers["X-PocketAI-Token"] = auth_token

    health_url = f"{server_url}/health"
    start_time = time.time()

    while time.time() - start_time < max_wait_sec:
        try:
            resp = requests.get(health_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                model_name = data.get("model_name", "Qwen3")
                model_loaded = data.get("model_loaded", False)
                runtime_status = data.get("runtime_status", "")

                if model_loaded or runtime_status == "ready":
                    return True, model_name
                # Model is warming up
                time.sleep(1)
        except Exception:
            time.sleep(1)

    return False, "Qwen3"


def send_chat_request(server_url: str, auth_token: str, question: str,
                      temperature: float, max_tokens: int, timeout: int,
                      max_retries: int, retry_delay: int) -> dict:
    """
    Sends question to POST /api/chat with configurable retries.
    """
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    if auth_token:
        headers["X-PocketAI-Token"] = auth_token

    payload = {
        "question": question,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    chat_url = f"{server_url}/api/chat"
    last_error = ""

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(chat_url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401:
                return {"success": False, "error": "Unauthorized: Authentication token mismatch"}
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text}"
        except requests.exceptions.Timeout:
            last_error = f"Request timed out after {timeout} seconds"
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {e}"
        except Exception as e:
            last_error = str(e)

        if attempt < max_retries:
            time.sleep(retry_delay)

    return {"success": False, "error": last_error}


def format_full_report(results: list[dict], model_name: str) -> str:
    """Formats all question-answer pairs cleanly for answer.txt and clipboard."""
    lines = [
        "================================================================================",
        " POCKETAI BRIDGE - OFFLINE AI INFERENCE REPORT",
        f" Model: {model_name} (Running 100% Offline on Phone)",
        f" Date:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "================================================================================",
        ""
    ]

    for idx, item in enumerate(results, 1):
        q = item.get("question", "")
        a = item.get("answer", "")
        duration = item.get("processing_time", 0.0)

        lines.append(f"QUESTION {idx}:")
        lines.append(f"{q}")
        lines.append("-" * 80)
        lines.append(f"{a}")
        lines.append("")
        lines.append(f"[Time: {duration}s]")
        lines.append("=" * 80)
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="PocketAI Bridge - Offline AI Terminal Client")
    parser.add_argument("file", nargs="?", default="test.txt", help="Input questions text file (default: test.txt)")
    parser.add_argument("--server", dest="server", default=None, help="Phone server URL (e.g. http://192.168.43.1:8800)")
    parser.add_argument("--token", dest="token", default=None, help="Authentication token if required")
    parser.add_argument("--out", dest="out", default=None, help="Output file name (default: answer.txt)")

    args = parser.parse_args()

    input_file = Path(args.file)
    if not input_file.is_absolute():
        input_file = SCRIPT_DIR / input_file

    config = load_config()

    server_url = args.server or config["server_url"]
    auth_token = args.token or config.get("auth_token", "")
    output_filename = args.out or config.get("output_file", "answer.txt")
    output_path = SCRIPT_DIR / output_filename
    timeout = config.get("timeout_seconds", 300)
    max_retries = config.get("max_retries", 3)
    retry_delay = config.get("retry_delay_seconds", 2)
    temperature = config.get("temperature", 0.6)
    max_tokens = config.get("max_tokens", 2048)
    do_copy = config.get("copy_to_clipboard", True)

    # 1. Read and validate questions
    questions = extract_questions(input_file)
    total_q = len(questions)

    # Expected Header Output
    print("========================================")
    print("POCKETAI BRIDGE")
    print("===============")
    print("")
    print("[+] Connecting to phone...")

    # 2. Connect to phone
    try:
        active_url = discover_server(server_url, auth_token)
    except ConnectionError:
        print("[!] Connection Failed.")
        print(f"    Could not reach PocketAI Server at {server_url}")
        print("\nTroubleshooting Steps:")
        print("1. Ensure Phone Hotspot is turned ON.")
        print("2. Ensure Laptop is connected to Phone's Hotspot Wi-Fi.")
        print("3. In Nexus App on phone, tap PocketAI Server and click 'Start Server'.")
        print("4. Verify IP address shown on phone screen matches config.json.")
        log_history(f"ERROR: Connection failed to {server_url}")
        sys.exit(1)

    print("[+] Checking API...")
    is_ready, model_name = check_and_wait_for_model(active_url, auth_token)

    print("[+] Phone connected.")
    print(f"[+] {model_name} loaded.")
    print("")

    log_history(f"SESSION START: {total_q} questions from {input_file.name} to {active_url} ({model_name})")

    results = []

    # 3. Process questions sequentially
    for i, question in enumerate(questions, 1):
        print(f"[{i}/{total_q}] Processing question...")
        log_history(f"REQ [{i}/{total_q}]: {question[:80]}")

        res = send_chat_request(
            server_url=active_url,
            auth_token=auth_token,
            question=question,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay
        )

        if res.get("success", False):
            answer = res.get("answer", "").strip()
            duration = res.get("processing_time", 0.0)
            item = {
                "question": question,
                "answer": answer,
                "processing_time": duration
            }
            results.append(item)
            log_history(f"RESP [{i}/{total_q}]: Success ({duration}s, {len(answer)} chars)")
            print("[+] Answer received.")
            print("")
        else:
            err = res.get("error", "Unknown inference failure")
            item = {
                "question": question,
                "answer": f"[ERROR GENERATING ANSWER: {err}]",
                "processing_time": 0.0
            }
            results.append(item)
            log_history(f"RESP [{i}/{total_q}]: FAILED - {err}")
            print(f"[!] Warning: Question {i} failed: {err}")
            print("")

        # Incremental save after each question so progress is never lost
        partial_report = format_full_report(results, model_name)
        try:
            output_path.write_text(partial_report, encoding="utf-8")
        except Exception as e:
            log_history(f"ERROR writing partial output: {e}")

    # 4. Final Output Formatting
    final_report = format_full_report(results, model_name)
    output_path.write_text(final_report, encoding="utf-8")

    # 5. Copy to clipboard
    clipboard_copied = False
    if do_copy and HAS_PYPERCLIP:
        try:
            pyperclip.copy(final_report)
            clipboard_copied = True
        except Exception as e:
            log_history(f"Clipboard copy warning: {e}")

    print("========================================")
    print("[✓] ALL QUESTIONS COMPLETED")
    print(f"[✓] {output_filename} CREATED")
    if clipboard_copied:
        print("[✓] CLIPBOARD COPIED")
    else:
        print("[*] OUTPUT SAVED TO FILE")
    print("====================")

    log_history(f"SESSION FINISHED: {len(results)}/{total_q} questions completed.")


if __name__ == "__main__":
    main()
