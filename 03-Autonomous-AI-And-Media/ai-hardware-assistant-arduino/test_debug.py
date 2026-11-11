# final_test_working.py
import serial
import time

print("🔄 Opening COM3...")

try:
    ser = serial.Serial('COM3', 9600, timeout=2)
    print("✅ Port opened")
    
    time.sleep(3)
    print("📥 Reading...")
    
    # Read for 5 seconds
    start = time.time()
    data_received = False
    
    while time.time() - start < 5:
        if ser.in_waiting:
            data = ser.readline().decode().strip()
            print(f"📥 {data}")
            data_received = True
        time.sleep(0.1)
    
    if data_received:
        print("\n✅✅✅ ARDUINO IS WORKING!")
        
        # Send PING
        print("\n📤 Sending PING...")
        ser.write(b"PING\n")
        time.sleep(1)
        
        # Read response
        while ser.in_waiting:
            resp = ser.readline().decode().strip()
            print(f"📥 {resp}")
    else:
        print("\n❌ NO DATA RECEIVED!")
        print("\n💡 CHECK:")
        print("1. Arduino code uploaded?")
        print("2. USB cable is DATA cable?")
        print("3. Arduino IDE closed?")
        print("4. Try different USB port")
    
    ser.close()
    
except Exception as e:
    print(f"❌ Error: {e}")