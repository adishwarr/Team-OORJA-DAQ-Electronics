# dashboard/backend/data_generator.py
import random

class FakeDataGenerator:
    def __init__(self):
        self.rpm = 1000
        self.speed = 0
        self.temp = 60
        # New State Variables
        self.battery_voltage = 52.0 # Volts
        self.battery_current = 0.0  # Amps
        self.soc = 100.0            # %
        self.motor_temp = 40.0
        self.battery_temp = 30.0

    def get_next_frame(self):
        # Simulate Physics
        target_rpm = 8000 if random.random() > 0.6 else 2000
        self.rpm += (target_rpm - self.rpm) * 0.05
        self.speed = self.rpm * 0.012  # Gear ratio

        # Simulate Power Draw
        # Current roughly proportional to RPM/Load
        target_current = (self.rpm / 8000) * 150 # Max 150 Amps
        self.battery_current += (target_current - self.battery_current) * 0.1
        
        # Voltage sag under load
        sag = self.battery_current * 0.05 # Resistance simulation
        self.battery_voltage = 52.0 - sag 

        # Power = V * I
        power = self.battery_voltage * self.battery_current

        # Temps (slow rise)
        self.motor_temp += self.battery_current * 0.001
        self.motor_temp -= (self.motor_temp - 40) * 0.01 # Cooling
        
        # Return complete dictionary
        return {
            "rpm": int(self.rpm),
            "speed": float(self.speed),
            "motor_temp": int(self.motor_temp),
            "battery_temp": int(self.battery_temp),
            "battery_voltage": round(self.battery_voltage, 1),
            "battery_current": round(self.battery_current, 1),
            "power": int(power),
            "soc": int(self.soc),
            "gps_lat": "34.0535 N",
            "gps_lon": "118.2450 W",
            "lap_time": "45.2s",
            "status": "CONNECTED"
        }