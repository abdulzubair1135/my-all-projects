import time
import random
import os
import subprocess

def run_pipeline_cycle():
    print("\n" + "=" * 50)
    print("[*] Starting Automation Cycle...")
    print("=" * 50)
    
    # Run pipeline in automated mode
    subprocess.run(["python", "stickman_pipeline.py"], check=False)

def main():
    print("[AUTOPILOT ENGINE STARTED]")
    while True:
        run_pipeline_cycle()
        
        # 1 to 4 hours random delay (seconds me: 3600 to 14400)
        delay_seconds = random.randint(3600, 14400)
        delay_hours = delay_seconds / 3600
        
        print(f"\n[SLEEP] Agla video upload hoga {delay_hours:.2f} ghante baad.")
        print(f"Waiting {delay_seconds} seconds...\n")
        time.sleep(delay_seconds)

if __name__ == "__main__":
    main()