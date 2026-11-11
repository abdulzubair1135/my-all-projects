with open('direct_deepseek.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """def get_deepseek_ws_url():
    \"\"\"Finds the open chat.deepseek.com tab and returns its webSocketDebuggerUrl.\"\"\"
    try:
        with urllib.request.urlopen(CDP_JSON_URL, timeout=3) as r:
            tabs = json.loads(r.read())
    except Exception as e:
        raise RuntimeError(f"Chrome is not running on port 9222: {e}")

    for t in tabs:
        url = t.get("url", "")
        if "chat.deepseek.com" in url and "webSocketDebuggerUrl" in t:
            return t["webSocketDebuggerUrl"]

    # If tab open but at deepseek.com home
    for t in tabs:
        if "deepseek.com" in t.get("url", "") and "webSocketDebuggerUrl" in t:
            return t["webSocketDebuggerUrl"]

    raise RuntimeError("DeepSeek tab not found in Chrome! Please open chat.deepseek.com in Chrome.")"""

replacement = """def ensure_chrome_ready():
    try:
        with urllib.request.urlopen(CDP_JSON_URL, timeout=2) as r:
            return json.loads(r.read())
    except Exception:
        pass

    import subprocess
    cmd = (
        r'cmd.exe /c start "" "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
        r'--remote-debugging-port=9222 --user-data-dir="C:\\chrome_dev" --no-first-run --no-default-browser-check '
        r'https://chat.deepseek.com https://studio.youtube.com'
    )
    subprocess.Popen(cmd, shell=True)
    for _ in range(8):
        time.sleep(1)
        try:
            with urllib.request.urlopen(CDP_JSON_URL, timeout=1) as r:
                return json.loads(r.read())
        except Exception:
            pass
    return []

def get_deepseek_ws_url():
    \"\"\"Finds the open chat.deepseek.com tab and returns its webSocketDebuggerUrl.\"\"\"
    tabs = ensure_chrome_ready()
    if not tabs:
        raise RuntimeError("Chrome is not running on port 9222!")

    for t in tabs:
        url = t.get("url", "")
        if "chat.deepseek.com" in url and "webSocketDebuggerUrl" in t:
            return t["webSocketDebuggerUrl"]

    for t in tabs:
        if "deepseek.com" in t.get("url", "") and "webSocketDebuggerUrl" in t:
            return t["webSocketDebuggerUrl"]

    raise RuntimeError("DeepSeek tab not found in Chrome! Please open chat.deepseek.com in Chrome.")"""

norm_text = text.replace('\r\n', '\n')
norm_target = target.replace('\r\n', '\n')

if norm_target in norm_text:
    new_text = norm_text.replace(norm_target, replacement)
    with open('direct_deepseek.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESS: direct_deepseek.py updated with auto-launch self-healing!")
else:
    print("FAILED: Target not matched")
