import subprocess
import time
import os

exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_dir = r"C:\chrome_dev"
cmd = f'"{exe}" --remote-debugging-port=9222 --user-data-dir="{user_dir}" --no-first-run --no-default-browser-check https://chat.deepseek.com'
print("Launching Chrome...")
subprocess.Popen(cmd, shell=True)
time.sleep(4)
print("Done!")
