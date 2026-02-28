import time
import math
import random

class TelemetryHandler:
    def __init__(self, port='COM3', baud_rate=115200):
        # Arguments are accepted to match backend structure but ignored
        self.start_time = time.time()
        print("⚠️ SIMULATION MODE STARTED: Generating 72V System Data...")

    def get_data(self):
        """
        Generates realistic 72V battery physics data.
        """
        # Time elapsed since start
        t = time.time() - self.start_time
        
        # --- PHYSICS SIMULATION ---
        
        # 1. Speed: Accelerates and decelerates (Sine wave 0 to 100 km/h)
        # Period is roughly 20 seconds
        speed = abs(math.sin(t * 0.3)) * 100
        
        # 2. RPM: Directly proportional to speed (approx 45 RPM per km/h) + random noise
        rpm = (speed * 45) + random.uniform(-50, 50)
        
        # 3. Voltage: 72V System Simulation (20S Li-Ion)
        # Max (84V) - Min (60V). 
        # We simulate a battery sitting around 76V that sags under load.
        # High speed = High Load = Voltage Drop (Sag)
        base_voltage = 76.0 
        sag = (speed / 100.0) * 7.0 # Up to 7V drop at max speed
        voltage = base_voltage - sag + random.uniform(-0.2, 0.2)
        
        # 4. Current: High speed/acceleration pulls more amps
        current = (speed / 100.0) * 85.0 + random.uniform(0, 2)

        # 5. Temperatures: Rise slowly over time
        motor_temp = 40 + (speed * 0.5) + (math.sin(t * 0.1) * 5)
        bat_temp = 30 + (t * 0.1)

        # 6. GPS: simulate driving in a circle
        lat = 30.34 + (math.sin(t * 0.1) * 0.0005)
        lon = 76.38 + (math.cos(t * 0.1) * 0.0005)

        # Return dictionary matching backend.py structure
        return {
            "lat": f"{lat:.4f}",
            "lon": f"{lon:.4f}",
            "voltage": voltage,
            "current": current,
            "bat_temp": bat_temp,
            "motor_temp": motor_temp,
            "speed": speed,
            "rpm": rpm,
            "connected": True
        }