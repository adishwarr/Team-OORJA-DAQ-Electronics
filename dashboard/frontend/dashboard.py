# frontend/dashboard.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from frontend.components.gauge import AnalogueGauge

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Go-Kart Telemetry MVP")
        self.setStyleSheet("background-color: #121212;") # Dark Mode
        self.resize(1000, 500)

        # --- Layout Assembly ---
        central_widget = QWidget()
        layout = QHBoxLayout() # Horizontal Layout
        
        # Create instances of our reusable component
        self.speed_dial = AnalogueGauge("SPEED", 0, 120, "km/h")
        self.rpm_dial = AnalogueGauge("RPM", 0, 10000, "RPM")
        self.temp_dial = AnalogueGauge("TEMP", 0, 120, "°C")

        # Add them to the layout
        layout.addWidget(self.speed_dial)
        layout.addWidget(self.rpm_dial) # Center stage
        layout.addWidget(self.temp_dial)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def update_ui(self, data):
        """Slot called by the backend signal"""
        self.rpm_dial.update_value(data['rpm'])
        self.speed_dial.update_value(data['speed'])
        self.temp_dial.update_value(data['temp'])