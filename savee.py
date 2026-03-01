import serial
import csv
import time
from datetime import datetime, timezone, timedelta
import os

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/cu.usbserial-10'  # Your Mac/Linux serial port
BAUD_RATE = 115200
CSV_FILE = 'oorja_telemetry.csv'
RAW_FILE = 'oorja_raw_dump.txt'

# Create a strict IST timezone object (UTC + 5:30)
ist_tz = timezone(timedelta(hours=5, minutes=30))

# These headers match the active, uncommented prints in your ESP32 code
HEADERS = [
    "Computer_Time_IST", 
    "Packet_ID", 
    "Speed_Kmph", 
    "RPM", 
    "LoRa_Timestamp", 
    "MPU_Gx", 
    "MPU_Gy", 
    "MPU_Gz"
]

def main():
    # 1. Initialize CSV file and write headers if it doesn't exist
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as csv_f:
        writer = csv.writer(csv_f)
        if not file_exists:
            writer.writerow(HEADERS)

    # 2. Open Serial Connection
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[*] Successfully connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        print("[*] Logging data... Press Ctrl+C to stop.")
    except serial.SerialException as e:
        print(f"[!] Error connecting to serial port: {e}")
        return

    # 3. Main Logging Loop
    try:
        # Open both files in append mode so we can write to them continuously
        with open(CSV_FILE, mode='a', newline='') as csv_f, open(RAW_FILE, mode='a') as raw_f:
            csv_writer = csv.writer(csv_f)
            
            while True:
                if ser.in_waiting > 0:
                    # Get exact computer time in 24hr IST format (HH:MM:SS.mmm)
                    current_ist = datetime.now(ist_tz).strftime('%H:%M:%S.%f')[:-3]
                    
                    # Read the raw byte line from ESP32
                    raw_bytes = ser.readline()
                    
                    try:
                        # Decode to string and strip newline characters
                        decoded_line = raw_bytes.decode('utf-8', errors='ignore').strip()
                    except Exception as e:
                        decoded_line = f"<DECODE ERROR: {raw_bytes}>"

                    # Skip empty lines
                    if not decoded_line:
                        continue

                    # --- LOG 1: RAW DUMP ---
                    # We write the exact string to the text file, appending the computer time for reference
                    raw_f.write(f"[{current_ist}] {decoded_line}\n")
                    raw_f.flush() # Force write to disk immediately

                    # --- LOG 2: CSV PARSING ---
                    # Only parse lines that look like our comma-separated telemetry
                    if "," in decoded_line and ">>>" not in decoded_line:
                        try:
                            # Split by comma and strip extra spaces from your C++ prints
                            data_values = [val.strip() for val in decoded_line.split(',')]
                            
                            # Ensure we have the exact number of data points expected (7 from ESP32)
                            if len(data_values) == 7:
                                # Prepend the computer time to the row
                                csv_row = [current_ist] + data_values
                                
                                # Write to CSV
                                csv_writer.writerow(csv_row)
                                csv_f.flush() # Force write to disk immediately
                                
                                # Optional: Print to terminal so you can see it working
                                print(f"Logged: {csv_row}")
                            else:
                                print(f"[!] Warning: Mismatched data length ({len(data_values)}). Saved to raw log only.")
                                
                        except Exception as e:
                            print(f"[!] CSV Parse Error: {e}. Saved to raw log only.")

    except KeyboardInterrupt:
        print("\n[*] Logging stopped by user.")
    finally:
        if ser.is_open:
            ser.close()
            print("[*] Serial port closed safely.")

if __name__ == '__main__':
    main()