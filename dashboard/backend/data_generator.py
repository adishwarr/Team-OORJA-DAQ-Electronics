# backend/data_generator.py
import random
import math

class FakeDataGenerator:
    def __init__(self):
        self.rpm = 1000
        self.speed = 0
        self.temp = 60

    def get_next_frame(self):
        """Simulates physics to return a dict of data"""
        
        # Simulate acceleration logic
        target = 8000 if random.random() > 0.6 else 2000
        
        # Physics smoothing (Lerp)
        self.rpm += (target - self.rpm) * 0.05
        self.speed = self.rpm * 0.015  # Simple gear ratio logic
        self.temp += (random.random() - 0.5) * 0.5 # Slow temp drift

        return {
            "rpm": int(self.rpm),
            "speed": int(self.speed),
            "temp": round(self.temp, 1)
        }