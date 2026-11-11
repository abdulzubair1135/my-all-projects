import os
import sys
import subprocess
import re
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
ADB = r"C:\Users\abdul\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(cmd):
    full_cmd = f'"{ADB}" {cmd}'
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip()

run_adb("shell uiautomator dump /sdcard/window_dump.xml")
run_adb("pull /sdcard/window_dump.xml ./scratch_window_dump.xml")

if os.path.exists("./scratch_window_dump.xml"):
    with open("./scratch_window_dump.xml", "r", encoding="utf-8") as f:
        content = f.read()
    root = ET.fromstring(content)
    for node in root.iter('node'):
        text = node.attrib.get('text', '')
        res_id = node.attrib.get('resource-id', '')
        bounds = node.attrib.get('bounds', '')
        clickable = node.attrib.get('clickable', '')
        if text or 'bottom' in res_id.lower() or 'tab' in res_id.lower() or 'nav' in res_id.lower():
            print(f"[{res_id}] text='{text}' bounds={bounds} clickable={clickable}")
