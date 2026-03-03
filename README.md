# 🏎️ Team OORJA — DAQ Electronics  

> **Telemetry Data Acquisition & Dashboard System**  
> Go-Kart Design Challenge (GKDC) | DAQ Department  

---

## 📖 Overview  

This repository contains the complete **Data Acquisition (DAQ) system** developed by the Electronics & DAQ department of **Team OORJA** for the **Go-Kart Design Challenge (GKDC)**.

The system enables real-time acquisition, transmission, storage, and visualization of critical vehicle telemetry data during testing and competition runs.

The stack spans embedded firmware, custom PCB hardware design, signal processing/simulation, and a live monitoring dashboard — enabling data-driven optimization of vehicle performance, driver inputs, and system reliability.

---

## 📁 Repository Structure  

```
Team-OORJA-DAQ-Electronics/
├── code/              # Embedded firmware & microcontroller code (C++)
├── dashboard/         # Real-time telemetry dashboard (Python)
├── simulation/        # Signal processing & sensor simulation (MATLAB)
├── PCB Design/        # Schematic files, PCB layout & 3D board model
├── images/            # Circuit diagrams, hardware photos, and screenshots
├── .gitignore
└── README.md
```

---

## ⚙️ System Architecture  

```
[ Sensors on Kart ]
        │
        ▼
[ Custom DAQ PCB ]
        │
        ▼
[ Microcontroller Firmware (C++) ]
        │
        ▼ (Serial / LoRa / Wireless)
[ Receiver / Data Logger ]
        │
        ▼
[ Python Dashboard ]
        │
        ▼
[ MATLAB Simulation & Analysis ]
```

---

## 🔧 Modules  

### `code/` — Embedded Firmware (C++)  

- Reads sensors (speed, temperature, voltage, current, throttle, brake)  
- Performs real-time data processing and filtering  
- Transmits telemetry over Serial / Wireless (LoRa/UART)  
- Logs data to onboard SD card (offline mode)  
- Implements fault detection and system monitoring  

---

### `dashboard/` — Telemetry Dashboard (Python)  

- Receives live telemetry data  
- Displays RPM, speed, battery parameters, lap count, etc.  
- Logs data to CSV/JSON  
- Provides structured visualization for track-side decision making  

---

### `simulation/` — MATLAB Simulation  

- Sensor signal modeling & noise analysis  
- Algorithm validation before hardware deployment  
- Lap-time and performance analysis  
- System response validation  

---

### `PCB Design/` — Hardware Design Files  

- Complete schematic diagrams  
- PCB layout files  
- Gerber outputs (if included)  
- 3D board model for mechanical integration  
- Optimized routing for noise reduction and automotive reliability  

Integrated subsystems:

- Microcontroller  
- Power regulation circuitry  
- Sensor input conditioning  
- Communication interfaces  
- SD card interface  
- Display & button connectors  

---

## 🛠️ Tech Stack  

| Layer | Technology |
|--------|------------|
| Embedded Firmware | C++ (Arduino / ESP32 / STM32 / Teensy) |
| Hardware Design | KiCad / Altium |
| Dashboard & Logging | Python (PySerial, Matplotlib / Tkinter) |
| Simulation & Analysis | MATLAB / Simulink |
| Communication | UART / CAN Bus / LoRa RF |

---

## 📊 Parameters Monitored  

- Battery Voltage & Current  
- Motor & Controller Temperature  
- RPM / Wheel Speed  
- Lap Counter  
- Throttle & Brake Position  
- GPS / Track Position *(if applicable)*  
- SD Card Data Logging  
- LoRa Telemetry Status  

---

## 🚀 Getting Started  

### Firmware  
1. Open `.ino` or `.cpp` in Arduino IDE / PlatformIO  
2. Select board and COM port  
3. Compile and upload  

### Dashboard  

```bash
cd dashboard
pip install -r requirements.txt
python dashboard.py
```

### Simulation  
Open `simulation/` in MATLAB and run the required `.m` file or Simulink model.

### PCB Design  
Open the `PCB Design/` folder in KiCad/Altium to view schematics and 3D board model.

---

## 👥 Team  

**Team OORJA — DAQ & Electronics Department**  
Go-Kart Design Challenge (GKDC)

> Built by student engineers integrating embedded systems, PCB design, RF telemetry, and motorsport analytics.

---

## 📄 License  

Developed for academic and competition purposes by Team OORJA.  
Please contact the team before reusing any part of this codebase.

---

## 📬 Contact  

For queries regarding the DAQ system, reach out via the team's official channels or open a GitHub Issue.
