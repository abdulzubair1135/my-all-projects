with open('auto_factory_batch.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """def launch_chrome_debugger():
    log("Chrome Debugger launch check...", "[CHROME]")
    chrome_paths = [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "chrome.exe"
    ]
    chosen_path = "chrome.exe"
    for cp in chrome_paths:
        if os.path.exists(cp):
            chosen_path = cp
            break

    cmd = (
        f'start "" "{chosen_path}" --remote-debugging-port=9222 '
        r'--user-data-dir="C:\\chrome_dev" --no-first-run --no-default-browser-check'
    )
    subprocess.Popen(cmd, shell=True)
    time.sleep(5)"""

replacement = """def launch_chrome_debugger():
    log("Chrome Debugger launch check...", "[CHROME]")
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2)
        log("Chrome already active on port 9222!", "[OK]")
        return True
    except Exception:
        pass

    chrome_paths = [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "chrome.exe"
    ]
    chosen_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    for cp in chrome_paths:
        if os.path.exists(cp):
            chosen_path = cp
            break

    cmd = (
        f'cmd.exe /c start "" "{chosen_path}" --remote-debugging-port=9222 '
        r'--user-data-dir="C:\\chrome_dev" --no-first-run --no-default-browser-check '
        r'https://chat.deepseek.com https://studio.youtube.com'
    )
    subprocess.Popen(cmd, shell=True)
    
    for _ in range(8):
        time.sleep(1)
        try:
            import urllib.request
            urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=1)
            log("Chrome Debugger successfully launched on port 9222!", "[OK]")
            return True
        except Exception:
            pass
    return False"""

norm_text = text.replace('\r\n', '\n')
norm_target = target.replace('\r\n', '\n')

if norm_target in norm_text:
    new_text = norm_text.replace(norm_target, replacement)
    with open('auto_factory_batch.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESS: auto_factory_batch.py updated!")
else:
    print("FAILED: Target not matched")
