# 🏎️ Team OORJA — DAQ Electronics

> **Telemetry Data Acquisition & Dashboard System**  
> Go-Kart Design Challenge (GKDC) | DAQ Department

---

## 📖 Overview

This repository contains the complete Data Acquisition (DAQ) system developed by the Electronics & DAQ department of **Team OORJA** for the **Go-Kart Design Challenge (GKDC)**. The system is responsible for real-time collection, transmission, and visualization of critical vehicle telemetry data during testing and competition runs.

The stack spans embedded firmware, signal processing/simulation, and a live monitoring dashboard — enabling the team to make data-driven decisions on vehicle performance, driver behavior, and system health.

---

## 📁 Repository Structure

```
Team-OORJA-DAQ-Electronics/
├── code/            # Embedded firmware & microcontroller code (C++)
├── dashboard/       # Real-time telemetry dashboard (Python)
├── simulation/      # Signal processing & sensor simulation (MATLAB)
├── images/          # Circuit diagrams, hardware photos, and screenshots
├── .gitignore
└── README.md
```

---

## ⚙️ System Architecture

```
[ Sensors on Kart ]
        │
        ▼
[ Microcontroller (C++) ]  ──── reads & packages sensor data
        │
        ▼ (Serial / Wireless)
[ Data Logger / Receiver ]
        │
        ▼
[ Python Dashboard ]  ──── live visualization & logging
        │
        ▼
[ MATLAB Simulation ]  ──── post-processing & model validation
```

---

## 🔧 Modules

### 1. `code/` — Embedded Firmware (C++)
Firmware running on the onboard microcontroller responsible for:
- Reading sensors (speed, temperature, voltage, current, etc.)
- Packaging and transmitting data over serial/wireless
- Onboard fault detection and alerting

### 2. `dashboard/` — Telemetry Dashboard (Python)
A real-time monitoring interface that:
- Receives live telemetry from the kart
- Displays key metrics (RPM, speed, battery voltage, lap time, etc.)
- Logs data to CSV/JSON for post-run analysis

### 3. `simulation/` — MATLAB Simulation
Used for:
- Sensor signal simulation and noise modeling
- Pre-deployment validation of DAQ algorithms
- Performance data analysis and lap time modeling

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Embedded Firmware | C++ (Arduino / ESP32 / STM32) |
| Dashboard & Logging | Python (PySerial, Matplotlib / Tkinter) |
| Simulation & Analysis | MATLAB / Simulink |
| Communication | UART / CAN Bus / RF Wireless |

---

## 🚀 Getting Started

### Prerequisites
- Arduino IDE or PlatformIO (for firmware)
- Python 3.8+
- MATLAB R2021a or later

### Firmware (C++)
```bash
# Open the relevant .ino or .cpp file in Arduino IDE / PlatformIO
# Select the correct board and COM port
# Upload to the microcontroller
```

### Dashboard (Python)
```bash
cd dashboard
pip install -r requirements.txt
python dashboard.py
```

### Simulation (MATLAB)
```
Open simulation/ in MATLAB
Run the relevant .m script or Simulink model
```

---

## 📊 Parameters Monitored

- 🔋 Battery Voltage & Current
- 🌡️ Motor & Controller Temperature
- ⚡ RPM / Wheel Speed
- 🏁 Lap Timer
- 🎛️ Throttle & Brake Position
- 📡 GPS / Track Position *(if applicable)*

---

## 👥 Team

**Team OORJA — DAQ & Electronics Department**  
Go-Kart Design Challenge (GKDC)

> *Built with passion by student engineers pushing the limits of embedded systems and motorsport telemetry.*

---

## 📄 License

This project is developed for academic and competition purposes by Team OORJA.  
Please contact the team before reusing any part of this codebase.

---

## 📬 Contact

For queries regarding the DAQ system, reach out via the team's official channels or open a GitHub Issue.
