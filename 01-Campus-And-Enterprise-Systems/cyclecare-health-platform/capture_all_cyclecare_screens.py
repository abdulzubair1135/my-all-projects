import os
import sys
import subprocess
import time

sys.stdout.reconfigure(encoding='utf-8')

ADB = r"C:\Users\abdul\AppData\Local\Android\Sdk\platform-tools\adb.exe"
OUT_DIR = os.path.abspath("CycleCare_Fresh_Screens")
os.makedirs(OUT_DIR, exist_ok=True)

def run_adb(cmd):
    full_cmd = f'"{ADB}" {cmd}'
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip()

def capture_screen(filename):
    remote_path = f"/sdcard/{filename}"
    run_adb(f"shell screencap -p {remote_path}")
    local_path = os.path.join(OUT_DIR, filename)
    run_adb(f"pull {remote_path} \"{local_path}\"")
    print(f"Captured: {filename}")
    return local_path

print("Starting complete screenshot capture...")

# 1. Bring MainActivity to foreground
print("Launching MainActivity...")
run_adb("shell am start -n com.cyclecare/.home.MainActivity")
time.sleep(2.0)

# Tab 1: Home Cycle Dial
print("Tapping Home tab (X=72, Y=1520)...")
run_adb("shell input tap 72 1520")
time.sleep(1.5)
capture_screen("screen_home_dial.png")

# Tab 2: Calendar
print("Tapping Calendar tab (X=216, Y=1520)...")
run_adb("shell input tap 216 1520")
time.sleep(1.5)
capture_screen("screen_calendar.png")

# Tab 4: Store Catalog
print("Tapping Store tab (X=504, Y=1520)...")
run_adb("shell input tap 504 1520")
time.sleep(1.5)
capture_screen("screen_store_catalog.png")

# Tab 5: Profile
print("Tapping Profile tab (X=648, Y=1520)...")
run_adb("shell input tap 648 1520")
time.sleep(1.5)
capture_screen("screen_profile.png")

# Tab 3: Plus / Log Modal
print("Tapping Plus tab (X=360, Y=1520)...")
run_adb("shell input tap 360 1520")
time.sleep(1.5)
capture_screen("screen_log_modal.png")
# Press back to close modal
run_adb("shell input keyevent 4")
time.sleep(1.0)

# Product Detail
print("Launching ProductDetailActivity...")
run_adb("shell am start -a android.intent.action.VIEW -d \"cyclecare://product\" com.cyclecare/.store.ProductDetailActivity")
time.sleep(2.0)
capture_screen("screen_product_detail.png")

# Partner Care
print("Launching PartnerCareActivity...")
run_adb("shell am start -n com.cyclecare/.partner.PartnerCareActivity")
time.sleep(2.0)
capture_screen("screen_partner_care.png")

# Order Tracking
print("Launching OrderTrackingActivity...")
run_adb("shell am start -n com.cyclecare/.partner.OrderTrackingActivity")
time.sleep(2.0)
capture_screen("screen_order_tracking.png")

# Delivery Agent
print("Launching DeliveryAgentActivity...")
run_adb("shell am start -n com.cyclecare/.partner.DeliveryAgentActivity")
time.sleep(2.0)
capture_screen("screen_delivery_agent.png")

print("All screenshots successfully captured!")
