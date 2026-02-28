import serial
import csv
import time
import math
import random

# RENAMED from TelemetryBackend to TelemetryHandler to match simulation.py
class TelemetryHandler: 
    def __init__(self, port='COM3', baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None
        self.simulation_mode = False
        self.start_time = time.time()
        
        # Internal state to hold current values
        self.current_data = {
            "speed": 0, "rpm": 0, "soc": 0,
            "voltage": 0, "current": 0, 
            "motor_temp": 0, "bat_temp": 0,
            "lat": "Waiting", "lon": "Waiting",
            "status": "INIT"
        }

        # Initialize Connection
        self.connect_serial()
        self.init_csv()

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            print(f"[Backend] Connected to {self.port}")
            self.simulation_mode = False
            self.current_data["status"] = "CONNECTED"
        except serial.SerialException:
            print(f"[Backend] Failed to connect to {self.port}. Switching to SIMULATION.")
            self.simulation_mode = True
            self.current_data["status"] = "SIMULATION"

    def init_csv(self):
        self.log_filename = f"telemetry_log_{int(time.time())}.csv"
        try:
            with open(self.log_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                header = ["packet_id", "lat", "lon", "voltage", "current", 
                          "bat_temp", "motor_temp", "speed_kph", "rpm", 
                          "dist_l", "dist_r", "steering", "timestamp", 
                          "mpu_gx", "mpu_gy", "mpu_gz"]
                writer.writerow(header)
        except Exception as e:
            print(f"[Backend] CSV Error: {e}")

    def get_data(self):
        """Called by dashboard.py to get the latest numbers"""
        if self.simulation_mode:
            self._generate_fake_data()
        else:
            self._read_serial_data()
            
        return self.current_data

    def _read_serial_data(self):
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                data = [x.strip() for x in line.split(',')]

                if len(data) >= 15:
                    with open(self.log_filename, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(data)

                    self.current_data["lat"] = data[1]
                    self.current_data["lon"] = data[2]
                    
                    try:
                        self.current_data["voltage"] = float(data[3])
                        self.current_data["current"] = float(data[4])
                        self.current_data["bat_temp"] = float(data[5])
                        self.current_data["motor_temp"] = float(data[6])
                        self.current_data["speed"] = float(data[7])
                        self.current_data["rpm"] = float(data[8])
                    except ValueError:
                        pass 

                    volts = self.current_data["voltage"]
                    self.current_data["soc"] = max(0, min(100, (volts - 60.0) / (24.0) * 100))
                    self.current_data["status"] = "LIVE DATA"
            except Exception as e:
                print(f"[Backend] Parse Error: {e}")

    # Add this method so backend works even if serial fails
    def _generate_fake_data(self):
         # Simple fallback if serial fails but we are using backend.py
         t = time.time() - self.start_time
         self.current_data['speed'] = abs(math.sin(t * 0.3)) * 50
         self.current_data['rpm'] = self.current_data['speed'] * 40
         self.current_data['voltage'] = 72 + math.sin(t)