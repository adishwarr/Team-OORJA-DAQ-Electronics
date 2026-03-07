//      OORJA RECEIVER (ESP32)

#include <HardwareSerial.h>


// ESP32 Serial2 is usually Pins 16 (RX) and 17 (TX)
#define LORA_SERIAL Serial2 
#define DEBUG_SERIAL Serial

struct OORJA {
  float latitude;
  float longitude;
  float bat_temp;
  float motor_temp;
  int speed_kph;
  float rpm;
  float current;
  float voltage;
  float dist_right;
  float dist_left;
  float steering_angle;
  uint32_t timestamp;
  float mpu_gx;
  float mpu_gy;
  float mpu_gz;
  uint32_t packet_id;
};


OORJA incomingData;

void setup() {
  initDebug();
  initLoRa();
}

void loop() {
  checkForIncomingData();
}

void initDebug() {
  DEBUG_SERIAL.begin(115200);
  delay(2000);
  DEBUG_SERIAL.println(">>> ESP32 RECEIVER LISTENING <<<");
}

void initLoRa() {
  // ESP32: .begin(baud, config, RX_pin, TX_pin)
  // Pin 16 is RX2, Pin 17 is TX2
  LORA_SERIAL.begin(9600, SERIAL_8N1, 16, 17);
}

void checkForIncomingData() {
  if (LORA_SERIAL.available() >= sizeof(OORJA)) {
    parsePacket();
    displayDashboard();
  }
}

void parsePacket() {
  LORA_SERIAL.readBytes((char*)&incomingData, sizeof(OORJA));
  
  // Clear any extra bytes to prevent buffer lag
  while(LORA_SERIAL.available() > 0) {
    LORA_SERIAL.read();
  }
}

void displayDashboard() {
  // Printing in a CSV-friendly format makes it much easier for your PC to save
  DEBUG_SERIAL.print(incomingData.packet_id); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.latitude, 5); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.longitude, 5); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.voltage); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.current); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.bat_temp); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.motor_temp); DEBUG_SERIAL.print(" ,");
  DEBUG_SERIAL.print(incomingData.speed_kph); DEBUG_SERIAL.print(" ,");
  DEBUG_SERIAL.print(incomingData.rpm); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.dist_left); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.dist_right); DEBUG_SERIAL.print(" ,");
  //DEBUG_SERIAL.print(incomingData.steering_angle); DEBUG_SERIAL.print(" ,");
  DEBUG_SERIAL.print(incomingData.timestamp); DEBUG_SERIAL.print(" ,");
  DEBUG_SERIAL.print(incomingData.mpu_gx); DEBUG_SERIAL.print(" ,");
  DEBUG_SERIAL.print(incomingData.mpu_gy); DEBUG_SERIAL.print(" ,");
  DEBUG_SERIAL.println(incomingData.mpu_gz);
} 