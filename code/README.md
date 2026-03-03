<h1>Transmitter.ino</h1><br>
runs on <b>teensy 4.1</b><br>
uses LoRa for real time transmittion and SD Card for offline data logging<br>
collects data from different sensors, processes the data and transmits it and saves it inside SD Card<br>
has push buttons for lap counter increment and decrement. uses Matrix display to show current lap<br><br><br>


<h1>RECEIVER_ESP.ino</h1><br>
Runs on ESP32
Uses LoRa for real-time data reception
Receives telemetry data from the transmitter node and processes it in real time
Displays live parameters on connected display interface
Stores received data for further analysis (optional SD/Flash storage support)
Implements wireless communication reliability checks (packet validation / RSSI monitoring)
Can interface with Wi-Fi for cloud upload or dashboard visualization
Designed for low-latency, high-reliability embedded telemetry applications
