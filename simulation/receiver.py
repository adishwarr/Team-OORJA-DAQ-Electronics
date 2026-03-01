import serial
import struct
import time
import math

# --- CONFIG ---
PORT = "COM9"      # Ensure MATLAB is on COM9
BAUD = 115200      # Matches your setup
RATE_HZ = 50       # Sending data 50 times per second

try:
    ser = serial.Serial(PORT, BAUD)
    print(f"Connected to {PORT}. Sending 'OORJA' Struct Data...")
except Exception as e:
    print(f"Error opening {PORT}: {e}")
    exit()

# Struct Format based on your ESP32 Code:
# 11 Floats (f), 1 Uint32 (I), 3 Floats (f), 1 Uint32 (I) = 64 Bytes
# Little Endian (<)
STRUCT_FMT = '<fffffffffffIfffI'

start_time = time.time()
packet_count = 0

try:
    while True:
        t = time.time() - start_time
        
        # --- 1. Generate Fake Data ---
        # GPS (Patiala coordinates)
        lat = 30.3527 + 0.0001 * math.sin(t * 0.5)
        lon = 76.3608 + 0.0001 * math.cos(t * 0.5)
        
        # Sensors
        bat_temp = 35.0 + math.sin(t)
        motor_temp = 45.0 + math.sin(t)
        speed_kph = 40.0 + 5 * math.sin(t)
        rpm = 3000 + 500 * math.sin(t)
        current = 15.0
        voltage = 48.0
        dist_right = 1.5
        dist_left = 1.5
        steering_angle = 30.0 * math.sin(t) # Steers left and right
        
        timestamp = int(t * 1000)
        
        # MPU6050 (IMU)
        mpu_gx = 0.1
        mpu_gy = 0.1
        mpu_gz = 9.8
        
        packet_id = packet_count

        # --- 2. Pack into 64 Bytes ---
        # Must match the order of 'struct OORJA' exactly!
        data = struct.pack(STRUCT_FMT, 
                           lat, lon, bat_temp, motor_temp, speed_kph, rpm, 
                           current, voltage, dist_right, dist_left, steering_angle, 
                           timestamp, mpu_gx, mpu_gy, mpu_gz, packet_id)

        # --- 3. Send ---
        ser.write(data)
        print(f"Sent Packet #{packet_id} | Steer: {steering_angle:.2f} | RPM: {rpm:.2f}")
        
        packet_count += 1
        time.sleep(1.0 / RATE_HZ)

except KeyboardInterrupt:
    ser.close()
    print("\nStopped.")