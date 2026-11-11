import os
import shutil

src_dir = "CycleCare_Fresh_Screens"
dst_dir = "CycleCare_Presentation_Assets"

files_to_copy = [
    ("fresh_home_dashboard.png", "device_screen_home_fresh.png"),
    ("fresh_product_detail.png", "device_screen_store_fresh.png"),
    ("fresh_order_tracking.png", "device_screen_order_tracking_fresh.png"),
    ("fresh_delivery_agent.png", "device_screen_delivery_agent_fresh.png"),
    ("fresh_partner_care.png", "device_screen_partner_fresh.png"),
    ("fresh_conversations.png", "device_screen_conversations_fresh.png"),
    ("fresh_chat.png", "device_screen_chat_fresh.png"),
]

for src, dst in files_to_copy:
    src_p = os.path.join(src_dir, src)
    dst_p = os.path.join(dst_dir, dst)
    if os.path.exists(src_p):
        shutil.copy2(src_p, dst_p)
        print(f"Copied {src} -> {dst}")
    else:
        print(f"Missing {src}")
print("Assets prepared successfully.")
