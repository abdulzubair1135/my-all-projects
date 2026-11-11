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
    print(f"Captured {filename}")
    return local_path

print("Starting fresh screenshot capture...")

# 1. Main / Home screen
print("1. Launching SplashActivity -> Home...")
run_adb("shell am start -n com.cyclecare/.auth.SplashActivity")
time.sleep(2.5)
capture_screen("fresh_home_dashboard.png")

# 2. Partner Care Activity
print("2. Launching PartnerCareActivity...")
run_adb("shell am start -n com.cyclecare/.partner.PartnerCareActivity")
time.sleep(2.0)
capture_screen("fresh_partner_care.png")

# 3. Product Detail Activity
print("3. Launching ProductDetailActivity...")
run_adb("shell am start -a android.intent.action.VIEW -d \"cyclecare://product\" com.cyclecare/.store.ProductDetailActivity")
time.sleep(2.0)
capture_screen("fresh_product_detail.png")

# 4. Delivery Agent Activity
print("4. Launching DeliveryAgentActivity...")
run_adb("shell am start -n com.cyclecare/.partner.DeliveryAgentActivity")
time.sleep(2.0)
capture_screen("fresh_delivery_agent.png")

# 5. Order Tracking Activity
print("5. Launching OrderTrackingActivity...")
run_adb("shell am start -n com.cyclecare/.partner.OrderTrackingActivity")
time.sleep(2.0)
capture_screen("fresh_order_tracking.png")

# 6. Circle Conversations Activity
print("6. Launching CircleConversationsActivity...")
run_adb("shell am start -n com.cyclecare/.chat.CircleConversationsActivity")
time.sleep(2.0)
capture_screen("fresh_conversations.png")

# 7. Circle Chat Activity
print("7. Launching CircleChatActivity...")
run_adb("shell am start -n com.cyclecare/.chat.CircleChatActivity")
time.sleep(2.0)
capture_screen("fresh_chat.png")

print("Screenshot capture batch completed!")
