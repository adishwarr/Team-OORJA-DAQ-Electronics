import numpy as np
import serial
import struct
import time

# --- CONFIG ---
PORT = "COM9" # Ensure this matches your MATLAB block!
BAUD = 115200
RATE_HZ = 50
DT = 1 / RATE_HZ

ser = serial.Serial(PORT, BAUD)
start_time = time.time()

# Initial GPS (Patiala/Thapar Region)
lat, lon = 30.3527, 76.3608 

print(f"LoRa Emulation Active on {PORT}. Sending data...")

try:
    while True:
        # 1. Generate Fake Physics (Circular Path)
        t = time.time() - start_time
        speed_m_s = 12.0 + np.sin(t) # Slight speed variation
        steer_deg = 20.0 * np.sin(t * 0.5) # Steering oscillates
        yaw_deg = (t * 40) % 360 # Continuous rotation
        
        # 2. Scale for Binary Packing (Matches your earlier logic)
        timestamp = int(t * 1000)
        wheel_rpm = int((speed_m_s / 0.3) * 60 / (2 * np.pi))
        steer_i = int(steer_deg * 100)
        yaw_i = int(yaw_deg * 100)
        ax_i = int(np.random.normal(0, 50)) # Random G-force noise
        lat_i = int((lat + 0.0001 * np.sin(t*0.1)) * 1e7)
        lon_i = int((lon + 0.0001 * np.cos(t*0.1)) * 1e7)
        speed_i = int(speed_m_s * 100)

        # 3. PACKING: <B I h h h h i i H (23 Bytes)
        # B=Header, I=Time, h=int16, i=int32, H=uint16
        packet = struct.pack('<B I h h h h i i H', 
                            0xAA, timestamp, wheel_rpm, steer_i, 
                            yaw_i, ax_i, lat_i, lon_i, speed_i)
        
        ser.write(packet)
        time.sleep(DT)
except KeyboardInterrupt:
    ser.close()
    print("Stopped.")