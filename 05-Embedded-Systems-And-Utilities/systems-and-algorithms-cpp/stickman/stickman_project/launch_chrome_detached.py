import subprocess
import time
import urllib.request
import json

exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_dir = r"C:\chrome_dev"
args = [
    exe,
    "--remote-debugging-port=9222",
    f"--user-data-dir={user_dir}",
    "--no-first-run",
    "--no-default-browser-check",
    "https://chat.deepseek.com"
]

print("Launching Chrome detached...")
p = subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
print(f"PID: {p.pid}")

for i in range(15):
    time.sleep(1)
    try:
        tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=1).read())
        print(f"SUCCESS! Port 9222 active with {len(tabs)} tabs!")
        for t in tabs:
            print(" -", t.get("url"))
        break
    except Exception as e:
        print(f"Waiting... ({i+1}) {e}")
