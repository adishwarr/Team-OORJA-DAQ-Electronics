# backend/data_manager.py
from PyQt6.QtCore import QThread, pyqtSignal
from backend.data_generator import FakeDataGenerator
import time

class DataManager(QThread):
    # This is the pipeline to the UI
    data_updated = pyqtSignal(dict) 

    def __init__(self):
        super().__init__()
        self.generator = FakeDataGenerator()
        self.is_running = True

    def run(self):
        """The main loop running in a separate thread"""
        while self.is_running:
            # 1. Fetch raw data
            raw_data = self.generator.get_next_frame()
            
            # 2. Process data (e.g., check for warning flags)
            processed_data = raw_data # Pass through for now
            
            # 3. Send to UI
            self.data_updated.emit(processed_data)
            
            # 4. Sleep to match refresh rate (e.g., 60FPS = ~16ms)
            self.msleep(16) 

    def stop(self):
        self.is_running = False