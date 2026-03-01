//OORJA TRANSMITTER (Teensy 4.1)

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <Fonts/FreeMonoOblique12pt7b.h>
#include <Fonts/FreeMonoBoldOblique9pt7b.h>
#include <Fonts/FreeMonoBold12pt7b.h>
#include <Fonts/FreeMono9pt7b.h>
#include <TinyGPS++.h>
#include <TimeLib.h> // Standard Teensy Time Library
#include <SD.h>
#include <DHT.h>




// --- CURRENT SENSOR GLOBALS ---
#define CURRENT_PIN 38
float zeroPointVoltage = 1.65;
const float sensitivity = 0.0066; // 6.6 mV/A (at 3.3V VCC)

// RPM GLOBALS (INTERRUPT DRIVEN)
#define RPM_PIN 32
volatile unsigned long lastPulseTime = 0; 
volatile unsigned long pulseInterval = 0; 
volatile bool newRpmData = false;  
float currentRPM = 0.0;

// Globals for SD Card
char logFileName[16]; // Stores "LOG_05.CSV"
bool sdReady = false;

#define GPS_SERIAL Serial3 
#define LORA_SERIAL Serial1
#define DEBUG_SERIAL Serial

const int UPDATE_INTERVAL = 500;
const int TRANSMISSION_INTERVAL = 800; // Send every 800ms

#define TFT_CS   10
#define TFT_DC    9
#define TFT_RST   8

#define PIN_TEMP_BAT   4
#define PIN_TEMP_MOTOR 5

struct OORJA {
  float latitude;
  float longitude;
  float bat_temp;
  float motor_temp;
  int speed_kph;
  float rpm;
  float current;
  float voltage;
  float dist_right = 999;
  float dist_left = 999;
  float steering_angle = 0;
  uint32_t timestamp = 00000000;
  float mpu_gx = 0.0;
  float mpu_gy = 0.0;
  float mpu_gz = 0.0;
  uint32_t packet_id = 0;
};

Adafruit_MPU6050 mpu;
Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);

#define PIN_LAP_INC 2  // Button to increase lap
#define PIN_LAP_DEC 3  // Button to decrease lap
#define GPS_BAUD 9600
int lap = 0;    
#include <FastLED.h>

// --- LED MATRIX CONFIG ---
#define LED_PIN     31      // Master Pinout
#define NUM_LEDS    64
#define BRIGHTNESS  124     // MAX Brightness for Sunlight is 255 (0 to 255)
#define LED_TYPE    WS2811
#define COLOR_ORDER RGB

CRGB leds[NUM_LEDS];

const uint8_t PROGMEM digits[10][8] = {
  {0x3C, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C}, // 0
  {0x08, 0x18, 0x28, 0x08, 0x08, 0x08, 0x08, 0x3E}, // 1
  {0x3C, 0x42, 0x02, 0x02, 0x3C, 0x40, 0x40, 0x7E}, // 2
  {0x3C, 0x42, 0x02, 0x3C, 0x02, 0x02, 0x42, 0x3C}, // 3
  {0x04, 0x0C, 0x14, 0x24, 0x44, 0x7E, 0x04, 0x04}, // 4
  {0x7E, 0x40, 0x40, 0x7C, 0x02, 0x02, 0x42, 0x3C}, // 5
  {0x3C, 0x42, 0x40, 0x7C, 0x42, 0x42, 0x42, 0x3C}, // 6
  {0x7E, 0x02, 0x04, 0x08, 0x10, 0x10, 0x10, 0x10}, // 7
  {0x3C, 0x42, 0x42, 0x3C, 0x42, 0x42, 0x42, 0x3C}, // 8
  {0x3C, 0x42, 0x42, 0x3E, 0x02, 0x02, 0x42, 0x3C}  // 9
};


// ULTRASONIC SENSORS
#define PIN_TRIG_L 20
#define PIN_ECHO_L 21
#define PIN_TRIG_R 22
#define PIN_ECHO_R 23

const unsigned long US_TIMEOUT = 25000; 

float currentDistL = 0.0;
float currentDistR = 0.0;

OORJA telemetry;
unsigned long lastSendTime1 = 0;
unsigned long lastSendTime2 = 0;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 1024;
int lastStateInc = HIGH;
int lastStateDec = HIGH;

TinyGPSPlus gps;

// Variables to hold last known valid location (optional fallback)
float currentLat = 10.54;
float currentLong = 77.30;
float currentSpeed = 0.0;

static const unsigned char PROGMEM image_battery_full_bits[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xff,0xff,0xff,0xff,0xfc,0x00,0xff,0xff,0xff,0xff,0xfc,0x03,0x00,0x00,0x00,0x00,0x03,0x03,0x00,0x00,0x00,0x00,0x03,0x03,0x3c,0xf3,0xcf,0x3c,0xf3,0x03,0x3c,0xf3,0xcf,0x3c,0xf3,0x3f,0x3c,0xf3,0xcf,0x3c,0xf3,0x3f,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0xc0,0x3c,0xf3,0xcf,0x3c,0xf3,0x3f,0x3c,0xf3,0xcf,0x3c,0xf3,0x3f,0x3c,0xf3,0xcf,0x3c,0xf3,0x03,0x3c,0xf3,0xcf,0x3c,0xf3,0x03,0x3c,0xf3,0xcf,0x3c,0xf3,0x03,0x00,0x00,0x00,0x00,0x03,0x03,0x00,0x00,0x00,0x00,0x03,0x00,0xff,0xff,0xff,0xff,0xfc,0x00,0xff,0xff,0xff,0xff,0xfc,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
static const unsigned char PROGMEM image_car_bits[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xff,0x00,0x00,0x00,0x3f,0xff,0x00,0x00,0x00,0xf0,0xc0,0xc0,0x00,0x00,0xf0,0xc0,0xc0,0x00,0x03,0xc0,0xc0,0x30,0x00,0x03,0xc0,0xc0,0x30,0x00,0x3f,0xff,0xff,0xff,0xf0,0x3f,0xff,0xff,0xff,0xf0,0xff,0x3f,0xff,0xf3,0xcc,0xff,0x3f,0xff,0xf3,0xcc,0xfc,0xcf,0xff,0xcc,0xfc,0xfc,0xcf,0xff,0xcc,0xfc,0x33,0x33,0xff,0x33,0x30,0x33,0x33,0xff,0x33,0x30,0x00,0xc0,0x00,0x0c,0x00,0x00,0xc0,0x00,0x0c,0x00};
static const unsigned char PROGMEM image_earth_bits[] = {0x07,0xc0,0x1e,0x70,0x27,0xf8,0x61,0xe4,0x43,0xe4,0x87,0xca,0x9f,0xf6,0xdf,0x82,0xdf,0x82,0xe3,0xc2,0x61,0xf4,0x70,0xf4,0x31,0xf8,0x1b,0xf0,0x07,0xc0,0x00,0x00};
static const unsigned char PROGMEM image_Layer_25_bits[] = {0xc3,0x80,0xc3,0x80,0xc1,0x80,0xc1,0x80,0xfd,0x80,0xfd,0x80,0xfd,0x80,0xe1,0x80,0xe1,0x80,0xe1,0x80,0x7d,0x80,0x7d,0x80,0x3d,0x80};
static const unsigned char PROGMEM image_location_bits[] = {0x00,0xff,0xc0,0x00,0x00,0xff,0xc0,0x00,0x0f,0x00,0x3c,0x00,0x0f,0x00,0x3c,0x00,0x30,0x00,0x03,0x00,0x30,0x00,0x03,0x00,0x30,0x3f,0x03,0x00,0x30,0x3f,0x03,0x00,0xc0,0xc0,0xc0,0xc0,0xc0,0xc0,0xc0,0xc0,0xc3,0x00,0x30,0xc0,0xc3,0x00,0x30,0xc0,0xc3,0x00,0x30,0xc0,0xc3,0x00,0x30,0xc0,0x33,0x00,0x33,0x00,0x33,0x00,0x33,0x00,0x30,0xc0,0xc3,0x00,0x30,0xc0,0xc3,0x00,0x0c,0x3f,0x0c,0x00,0x0c,0x3f,0x0c,0x00,0x0c,0x00,0x0c,0x00,0x0c,0x00,0x0c,0x00,0x03,0x00,0x30,0x00,0x03,0x00,0x30,0x00,0x00,0xc0,0xc0,0x00,0x00,0xc0,0xc0,0x00,0x00,0x33,0x00,0x00,0x00,0x33,0x00,0x00,0x00,0x3f,0x00,0x00,0x00,0x3f,0x00,0x00,0x00,0x0c,0x00,0x00,0x00,0x0c,0x00,0x00};
static const unsigned char PROGMEM image_operation_warning_bits[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x03,0xc0,0x00,0x00,0x03,0xc0,0x00,0x00,0x0c,0x30,0x00,0x00,0x0c,0x30,0x00,0x00,0x0c,0x30,0x00,0x00,0x0c,0x30,0x00,0x00,0x30,0x0c,0x00,0x00,0x30,0x0c,0x00,0x00,0xc3,0xc3,0x00,0x00,0xc3,0xc3,0x00,0x00,0xc3,0xc3,0x00,0x00,0xc3,0xc3,0x00,0x03,0x03,0xc0,0xc0,0x03,0x03,0xc0,0xc0,0x03,0x03,0xc0,0xc0,0x03,0x03,0xc0,0xc0,0x0c,0x03,0xc0,0x30,0x0c,0x03,0xc0,0x30,0x30,0x00,0x00,0x0c,0x30,0x00,0x00,0x0c,0x30,0x03,0xc0,0x0c,0x30,0x03,0xc0,0x0c,0xc0,0x03,0xc0,0x03,0xc0,0x03,0xc0,0x03,0xc0,0x00,0x00,0x03,0xc0,0x00,0x00,0x03,0x3f,0xff,0xff,0xfc,0x3f,0xff,0xff,0xfc,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
static const unsigned char PROGMEM image_weather_temperature_bits[] = {0x03,0xf0,0x00,0x00,0x03,0xf0,0x00,0x00,0x0c,0x0c,0x00,0x0c,0x0c,0x0c,0x00,0x0c,0x0c,0xcf,0x00,0x33,0x0c,0xcf,0x00,0x33,0x0c,0xcc,0x00,0x0c,0x0c,0xcc,0x00,0x0c,0x0c,0xcf,0x0f,0xc0,0x0c,0xcf,0x0f,0xc0,0x0c,0xcc,0x3c,0x00,0x0c,0xcc,0x3c,0x00,0x0c,0xcf,0x30,0x00,0x0c,0xcf,0x30,0x00,0x0c,0xcc,0x30,0x00,0x0c,0xcc,0x30,0x00,0x0c,0xcc,0x3c,0x00,0x0c,0xcc,0x3c,0x00,0x30,0xc3,0x0f,0xc0,0x30,0xc3,0x0f,0xc0,0xc3,0xf0,0xc0,0x00,0xc3,0xf0,0xc0,0x00,0xcc,0xfc,0xc0,0x00,0xcc,0xfc,0xc0,0x00,0xcf,0xfc,0xc0,0x00,0xcf,0xfc,0xc0,0x00,0xc3,0xf0,0xc0,0x00,0xc3,0xf0,0xc0,0x00,0x30,0x03,0x00,0x00,0x30,0x03,0x00,0x00,0x0f,0xfc,0x00,0x00,0x0f,0xfc,0x00,0x00};


#include <DHT.h>

// CHANGE TYPE TO DHT22
#define DHTTYPE DHT22 

// Initialize DHT sensors on the existing pins (4 and 5)
DHT dhtBat(PIN_TEMP_BAT, DHTTYPE);
DHT dhtMotor(PIN_TEMP_MOTOR, DHTTYPE);
float currentMotorTemp = 0.0;
float currentBatTemp = 0.0;



void setup() {
  analogReadResolution(12);
  initDebug();
  initLoRa();
  initGPS();
  initTFT();
  initMpu();
  initButtons();
  initMatrix();
  initTemps();
  initRTC();
  initSD(); 
  initUltrasonic();
  initRPM();
  initCurrentSensor();
}

void loop() {

  updateGPS();

  unsigned long currentTime1 = millis();
  if (currentTime1 - lastSendTime1 >= TRANSMISSION_INTERVAL) {
    lastSendTime1 = currentTime1;

    runTransmitterCycle();
    logToSD();

  }
  unsigned long currentTime2 = millis();
  if (currentTime2 - lastSendTime2 >= UPDATE_INTERVAL) {
    lastSendTime2 = currentTime2;

    updateUltrasonic();
    updateDisplayValues();

  }

  updateLapCounter();

}

void initGPS() {
  GPS_SERIAL.begin(GPS_BAUD);
  DEBUG_SERIAL.println(">>> GPS Initialized on Serial3 <<<");
}

void initTFT(){
  tft.begin();
  tft.setRotation(3);
  drawStaticLayout();
}

void initDebug() {
  DEBUG_SERIAL.begin(115200);
  delay(2000);
  DEBUG_SERIAL.println(">>> OORJA SYSTEM STARTING <<<");
}

void initLoRa() {
  LORA_SERIAL.begin(9600); // Default E32 baud rate
  DEBUG_SERIAL.println(">>> LoRa Initialized on Serial1 <<<");
}

void initMpu() {
  Serial.println("Initializing MPU6050...");

  if (!mpu.begin(0x68)) {
    Serial.println("Failed to find MPU6050 chip! Check wiring.");
    // while (1) { delay(10); }
  }

  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_5_HZ);
  
  Serial.println("MPU6050 Ready!");
}

void initButtons() {
  // INPUT_PULLUP enables the internal resistor. 
  // The pin reads HIGH when open, and LOW when pressed.
  pinMode(PIN_LAP_INC, INPUT_PULLUP);
  pinMode(PIN_LAP_DEC, INPUT_PULLUP);
}

void initTemps() {
  dhtBat.begin();
  dhtMotor.begin();
  
  // Take an initial reading to populate variables
  float tBat = dhtBat.readTemperature();
  float tMotor = dhtMotor.readTemperature();

  // "isnan" checks if the reading failed (is Not A Number)
  if (!isnan(tBat)) currentBatTemp = tBat;
  if (!isnan(tMotor)) currentMotorTemp = tMotor;

  DEBUG_SERIAL.println(">>> DHT22 Temp Sensors Initialized on Pins 4 & 5 <<<");
}

void initRTC() {
  // Connect the TimeLib to the Teensy's internal hardware clock
  setSyncProvider(getTeensy3Time);

  if (timeStatus() != timeSet) {
    DEBUG_SERIAL.println("RTC Not Set (Will default to 1970 until GPS Fix)");
  } else {
    DEBUG_SERIAL.println("RTC Initialized");
  }
}

void initUltrasonic() {
  pinMode(PIN_TRIG_L, OUTPUT);
  pinMode(PIN_ECHO_L, INPUT);
  pinMode(PIN_TRIG_R, OUTPUT);
  pinMode(PIN_ECHO_R, INPUT);

  // Ensure triggers are low to start
  digitalWrite(PIN_TRIG_L, LOW);
  digitalWrite(PIN_TRIG_R, LOW);

  DEBUG_SERIAL.println(">>> Ultrasonic Sensors Initialized (Pins 20-23) <<<");
}

// --- SD CARD MODULE ---

void initSD() {
  DEBUG_SERIAL.print("Initializing SD card...");

  // BUILTIN_SDCARD is a special internal pin definition for Teensy 4.1
  if (!SD.begin(BUILTIN_SDCARD)) {
    DEBUG_SERIAL.println("Card failed, or not present.");
    sdReady = false;
    return;
  }
  
  DEBUG_SERIAL.println("card initialized.");
  sdReady = true;

  strcpy(logFileName, "LOG_00.CSV");
  for (uint8_t i = 0; i < 100; i++) {
    logFileName[4] = i / 10 + '0';
    logFileName[5] = i % 10 + '0';
    if (!SD.exists(logFileName)) {
      break; 
    }
  }

  DEBUG_SERIAL.print("Logging to: ");
  DEBUG_SERIAL.println(logFileName);

  // This writes the column names at the top of the file
  File dataFile = SD.open(logFileName, FILE_WRITE);
  if (dataFile) {
    dataFile.println("PacketID,Timestamp,Lat,Long,Speed,RPM,BatTemp,MotorTemp,Current,Volts,DistR,DistL,Gx,Gy,Gz,Lap");
    dataFile.close();
  }
}

// --- RPM MODULE (Interrupt Driven & Non-Blocking) ---

void initRPM() {
  pinMode(RPM_PIN, INPUT_PULLUP);
  
  attachInterrupt(digitalPinToInterrupt(RPM_PIN), rpm_ISR, FALLING);
  
  DEBUG_SERIAL.println(">>> RPM Interrupt Initialized on Pin 32 <<<");
}


// ISR: This runs AUTOMATICALLY when Magnet Passes
void rpm_ISR() {
  unsigned long now = micros();
  unsigned long diff = now - lastPulseTime;
  
  if (diff > 4000) {
    pulseInterval = diff;
    lastPulseTime = now;
    newRpmData = true;
  }
}

void calculateRPM() {

  unsigned long timeSinceLastPulse = micros() - lastPulseTime;
  
  if (timeSinceLastPulse > 1000000) {
    currentRPM = 0.0;
    return;
  }

  if (newRpmData) {
    noInterrupts();
    unsigned long validInterval = pulseInterval;
    newRpmData = false;
    interrupts();
    
    float rawRPM = 60000000.0 / validInterval;
    
    currentRPM = ((int)(rawRPM * 10)) / 10.0;
  }
}

void logToSD() {
  if (!sdReady) return; 

  // Open file in Append mode
  File dataFile = SD.open(logFileName, FILE_WRITE);

  if (dataFile) {
    // Write data strictly in CSV format
    dataFile.print(telemetry.packet_id); dataFile.print(",");
    dataFile.print(telemetry.timestamp); dataFile.print(",");
    
    // Float precision: 6 decimals for GPS, 1 for sensors
    dataFile.print(telemetry.latitude, 4); dataFile.print(",");
    dataFile.print(telemetry.longitude, 4); dataFile.print(",");
    
    dataFile.print(telemetry.speed_kph); dataFile.print(",");
    dataFile.print(telemetry.rpm, 1); dataFile.print(",");
    
    dataFile.print(telemetry.bat_temp, 1); dataFile.print(",");
    dataFile.print(telemetry.motor_temp, 1); dataFile.print(",");
    
    dataFile.print(telemetry.current, 1); dataFile.print(",");
    dataFile.print(telemetry.voltage, 1); dataFile.print(",");
    
    dataFile.print(telemetry.dist_right, 1); dataFile.print(",");
    dataFile.print(telemetry.dist_left, 1); dataFile.print(",");
    
    dataFile.print(telemetry.mpu_gx); dataFile.print(",");
    dataFile.print(telemetry.mpu_gy); dataFile.print(",");
    dataFile.print(telemetry.mpu_gz); dataFile.print(",");
    
    dataFile.print(lap); // Add the global Lap variable
    
    dataFile.println(); 
    
    dataFile.close();   
  } else {
    // If write fails, flag error (try to recover next loop)
    DEBUG_SERIAL.println("Error writing to log file");
    if (!SD.exists(logFileName)) sdReady = false; 
  }
}




void updateUltrasonic() {

  currentDistL = readDistance(PIN_TRIG_L, PIN_ECHO_L);

  delayMicroseconds(50); 

  currentDistR = readDistance(PIN_TRIG_R, PIN_ECHO_R);
    
  DEBUG_SERIAL.print("L: "); DEBUG_SERIAL.print(currentDistL);
  DEBUG_SERIAL.print("cm | R: "); DEBUG_SERIAL.println(currentDistR);
}

float readDistance(int trigPin, int echoPin) {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  

  long duration = pulseIn(echoPin, HIGH, US_TIMEOUT);
  

  if (duration == 0) {
    return 0.0; 
  } else {

    return (duration * 0.0343) / 2.0;
  }
}

float getDistL() { return currentDistL; }
float getDistR() { return currentDistR; }

time_t getTeensy3Time() {
  return Teensy3Clock.get();
}

uint32_t getEpochTime() {
  return (uint32_t)now(); 
}

void syncRTCtoGPS() {
  // Only sync if GPS time is valid AND we haven't synced recently 
  // (Syncing too often is unnecessary)
  static unsigned long lastSyncTime = 0;
  const unsigned long SYNC_INTERVAL = 600000; // Check every 600 seconds

  if (millis() - lastSyncTime > SYNC_INTERVAL) {
    lastSyncTime = millis(); // Reset timer
    
    // Check if GPS has a valid date and time
    if (gps.date.isValid() && gps.time.isValid() && gps.date.year() > 2025) {
      
      // 1. Create a standard time variable from GPS data
      tmElements_t tm;
      tm.Year = CalendarYrToTm(gps.date.year());
      tm.Month = gps.date.month();
      tm.Day = gps.date.day();
      tm.Hour = gps.time.hour();
      tm.Minute = gps.time.minute();
      tm.Second = gps.time.second();
      
      time_t gpsTime = makeTime(tm);

      // 2. Set the Teensy Hardware RTC
      Teensy3Clock.set(gpsTime); 
      
      // 3. Resync the software library
      setTime(gpsTime);
      
      DEBUG_SERIAL.println(">>> RTC Synced with GPS Time <<<");
    }
  }
}




void updateTemps() {
    float newBat = dhtBat.readTemperature();
    float newMotor = dhtMotor.readTemperature();

    if (!isnan(newBat)) {
      currentBatTemp = newBat;
    }
    
    if (!isnan(newMotor)) {
      currentMotorTemp = newMotor;
    }
    
    // DEBUG_SERIAL.print("Bat: "); DEBUG_SERIAL.print(currentBatTemp);
    // DEBUG_SERIAL.print("C | Motor: "); DEBUG_SERIAL.println(currentMotorTemp);
}


float BatTemp() {
  return currentBatTemp;
}

float MotorTemp() {
  return currentMotorTemp;
}

void updateGPS() {
  while (GPS_SERIAL.available() > 0) {
    gps.encode(GPS_SERIAL.read());
  }
}

float getLat() {
  if (gps.location.isValid()) {
    currentLat = gps.location.lat();
    return currentLat;
  }
  return currentLat; // Return last known valid if signal lost
}

float getLong() {
  if (gps.location.isValid()) {
    currentLong = gps.location.lng();
    return currentLong;
  }
  return currentLong;
}

float getGPS_Speed() {
  if (gps.speed.isValid()) {
    currentSpeed = gps.speed.kmph(); // Returns Speed in KM/H
    return currentSpeed;
  }
  return 0.0;
}

// Gyroscope Getters (Returns rad/s)
float getgx() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  return g.gyro.x;
}

float getgy() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  return g.gyro.y;
}

float getgz() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  return g.gyro.z;
}

void runTransmitterCycle() {
    acquireSensorData(); // Read Sensors
    transmitPacket();    // Send Data
    debugPrint();        // Print locally for checking
}

void acquireSensorData() {
  telemetry.packet_id = telemetry.packet_id + (uint32_t)1 ;

  telemetry.latitude = getLat(); 
  telemetry.longitude = getLong();

  updateTemps();
  telemetry.bat_temp = BatTemp();
  telemetry.motor_temp = MotorTemp();

  updateGPS();
  calculateRPM();
  
  telemetry.rpm = currentRPM;
  telemetry.speed_kph = telemetry.speed_kph = (int)((currentRPM * PI * 0.277 * 60.0) / 1000.0); 

  telemetry.current = readCurrent();
  telemetry.voltage = 70.8;

  telemetry.dist_right = getDistR();
  telemetry.dist_left = getDistL();

  telemetry.steering_angle = 0;
  syncRTCtoGPS();
  telemetry.timestamp = getEpochTime();

  telemetry.mpu_gx = getgx();
  telemetry.mpu_gy = getgy();
  telemetry.mpu_gz = getgz();

}

void transmitPacket() {
  LORA_SERIAL.write((uint8_t*)&telemetry, sizeof(OORJA));
}

void updateLapCounter() {
  int readingInc = digitalRead(PIN_LAP_INC);
  int readingDec = digitalRead(PIN_LAP_DEC);

  if ((millis() - lastDebounceTime) > debounceDelay) {

    if (readingInc == LOW && lastStateInc == HIGH) {
      lap++; 
      DEBUG_SERIAL.print("Lap Increment: ");
      DEBUG_SERIAL.println(lap);
      updateLapMatrix(lap);
      lastDebounceTime = millis(); // Reset timer
    }
    else if (readingDec == LOW && lastStateDec == HIGH) {
      lap--;
      if (lap < 0) {
        lap = 0; 
      }
      DEBUG_SERIAL.print("Lap Decrement: ");
      DEBUG_SERIAL.println(lap);
      updateLapMatrix(lap);
      lastDebounceTime = millis(); 
    }
  }

  lastStateInc = readingInc;
  lastStateDec = readingDec;
}

void debugPrint() {
  DEBUG_SERIAL.print("[TX] Sent Packet ID: ");
  DEBUG_SERIAL.println(telemetry.packet_id);
  DEBUG_SERIAL.print(" LAP "); DEBUG_SERIAL.println(lap);
}

void drawStaticLayout(void) {
    tft.fillScreen(0x0); // Black Background

    // Header Lines
    tft.drawLine(0, 20, 320, 20, 0x971F);
    tft.drawLine(57, 0, 57, 19, 0x971F);

    // Header Text
    tft.setTextColor(0x371);
    tft.setTextWrap(false);
    tft.setFont(&FreeMonoOblique12pt7b);
    tft.setCursor(90, 15);
    tft.print("Team Oorja");

    // Icons
    tft.drawBitmap(271, 2, image_earth_bits, 15, 16, 0xFFFF);
    tft.drawCircle(160, 95, 72, 0xB0C0); // Center Speed Circle
    tft.drawBitmap(141, 20, image_car_bits, 38, 32, 0x371);
    tft.drawBitmap(35, 25, image_location_bits, 26, 32, 0xE8EC);
    tft.drawBitmap(260, 25, image_weather_temperature_bits, 32, 32, 0x2BA);
    
    // Labels: Battery/Motor
    tft.setTextColor(0xBDF7);
    tft.setFont(); // Reset to default font for small text
    tft.setCursor(233, 62);
    tft.print("Battery");
    tft.setCursor(239, 73);
    tft.print("Motor");

    // Lines
    tft.drawLine(0, 0, 0, 0, 0xE120);
    tft.drawLine(0, 84, 88, 84, 0x971F);
    tft.drawLine(232, 85, 320, 85, 0x971F);

    // Battery Icon
    tft.drawBitmap(20, 100, image_battery_full_bits, 48, 32, 0x75C8);

    // Vertical Separator
    tft.drawLine(159, 239, 159, 168, 0x971F);

    // Current/Voltage Labels
    tft.setTextColor(0xFFFF); // Reset color to White for text
    tft.setFont(&FreeMonoBoldOblique9pt7b);
    tft.setCursor(5, 155);
    tft.print("Current");
    tft.setCursor(5, 201);
    tft.print("Voltage");

    // Thunderbolt Icon
    tft.drawBitmap(15, 3, image_Layer_25_bits, 9, 13, 0xE120);

    // Warning Icon
    tft.drawBitmap(251, 96, image_operation_warning_bits, 32, 32, 0xF760);

    // Collision Label
    tft.setTextColor(0xBDF7);
    tft.setFont(); // Default font
    tft.setCursor(241, 136);
    tft.print("Collision");

    // Collision Box Outlines
    tft.drawRect(211, 162, 100, 23, 0xFFFF);
    tft.drawRect(212, 205, 100, 23, 0xFFFF);

    // Collision Labels (R/L)
    tft.setTextColor(0xFFFF);
    tft.setFont(&FreeMono9pt7b);
    tft.setCursor(216, 178);
    tft.print("R");
    tft.setCursor(217, 221);
    tft.print("L");

    // Units Labels
    tft.setTextColor(0xEF7D);
    tft.setFont(&FreeMonoBold12pt7b);
    tft.setCursor(138, 118); // "Kmph" Position adjusted manually if needed
    tft.setTextSize(1);
    tft.print("Kmph");

    // Cardinal Directions
    tft.setTextColor(0xFFFF);
    tft.setFont(); // Default
    tft.setCursor(81, 62); tft.print("N");
    tft.setCursor(81, 73); tft.print("E");
    tft.setCursor(310, 62); tft.print("C");
    tft.setCursor(310, 73); tft.print("C");

    // Amps/Volts Units
    tft.setFont(&FreeMonoBoldOblique9pt7b);
    tft.setCursor(95, 172); tft.print("A");
    tft.setCursor(95, 220); tft.print("V");
}

void updateDisplayValues() {
    
    // NOTE: When using custom fonts, we cannot use text background colors to overwrite.
    // We must use fillRect to clear the previous number before printing the new one.
    
    // 1. SPEED (Center)
    tft.fillRect(60, 60, 100, 50, 0x0); // Clear Area (Approximate box based on visual)
    tft.setTextColor(0xFFFF);
    tft.setTextSize(3); // Based on original code
    tft.setFont(&FreeMonoBoldOblique9pt7b);
    tft.setCursor(89, 102);
    tft.print(telemetry.speed_kph);

    // 2. RPM (Below Car)
    tft.fillRect(115, 125, 100, 25, 0x0); // Clear Area
    tft.setTextColor(0xEF7D);
    tft.setTextSize(1);
    tft.setFont(&FreeMonoBold12pt7b);
    tft.setCursor(118, 147);
    tft.print(telemetry.rpm, 1);

    // 3. Latitude & Longitude
    tft.setFont(); // Default Font
    tft.setTextColor(0xFFFF);
    
    tft.fillRect(14, 62, 65, 8, 0x0); // Clear Lat
    tft.setCursor(14, 62);
    tft.print(telemetry.latitude, 7);

    tft.fillRect(14, 73, 65, 8, 0x0); // Clear Long
    tft.setCursor(14, 73);
    tft.print(telemetry.longitude, 7);

    // 4. Temperatures
    tft.fillRect(280, 62, 30, 8, 0x0); // Clear Bat Temp
    tft.setCursor(280, 62);
    tft.print(telemetry.bat_temp, 1);

    tft.fillRect(280, 73, 30, 8, 0x0); // Clear Motor Temp
    tft.setCursor(280, 73);
    tft.print(telemetry.motor_temp, 1);

    // 5. Current & Voltage
    tft.setFont(&FreeMono9pt7b); // Using 9pt for these values
    tft.setTextColor(0xFFFF);

    tft.fillRect(40, 158, 50, 20, 0x0); // Clear Current
    tft.setCursor(40, 173);
    tft.print(telemetry.current, 1);

    tft.fillRect(40, 205, 50, 20, 0x0); // Clear Voltage
    tft.setCursor(40, 220);
    tft.print(telemetry.voltage, 1);

    // 6. Distance Values (Right/Left)
    tft.fillRect(165, 160, 45, 20, 0x0); // Clear Dist Right
    tft.setCursor(165, 179);
    tft.print(telemetry.dist_right, 1);

    tft.fillRect(165, 205, 45, 20, 0x0); // Clear Dist Left
    tft.setCursor(165, 222);
    tft.print(telemetry.dist_left, 1);

    // 7. Dynamic Collision Bars
    // Map distance (0-400cm) to bar width (0-89px)
    // Adjust mapping logic based on your sensor range
    int width_R = map(constrain((int)telemetry.dist_right, 0, 400), 0, 400, 0, 89);
    int width_L = map(constrain((int)telemetry.dist_left, 0, 400), 0, 400, 0, 89);

    // Clear inside of bars first
    tft.fillRect(212+1, 164, 98, 19, 0x0); // Clear R
    tft.fillRect(214+1, 207, 98, 19, 0x0); // Clear L

    // Draw new bars
    tft.fillRect(212+1, 164, width_R, 19, 0xFB0A);
    tft.fillRect(214+1, 207, width_L, 19, 0xFB0A);
}  



//LED MATRIX MODULE (FastLED)

void initMatrix() {
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  
  // Start with Lap 0
  updateLapMatrix(0);
  
  DEBUG_SERIAL.println("LED Matrix Initialized on Pin 31");
}

void updateLapMatrix(int num) {
  if (num > 9) num = 9; 
  if (num < 0) num = 0;

  FastLED.clear();
  

  for (int row = 0; row < 8; row++) {
    uint8_t rowData = pgm_read_byte(&(digits[num][row]));
    
    for (int col = 0; col < 8; col++) {
      if (rowData & (1 << (7 - col))) {
        
        // Linear Mapping (Row * 8 + Col)
        int index = (row * 8) + col; 
        
        // SET COLOR: Pure Red for Sunlight
        leds[index] = CRGB::Red; 
      }
    }
  }
  FastLED.show();
}

// CURRENT SENSOR MODULE (ACS758)

void initCurrentSensor() {
  pinMode(CURRENT_PIN, INPUT);
  
  // CALIBRATION ROUTINE
  // We take 10 readings at startup to find the "Zero Amp" baseline.

  long totalRaw = 0;
  for(int i=0; i<10; i++) {
    totalRaw += analogRead(CURRENT_PIN);
    delay(10);
  }
  
  // Average raw value (0-4095)
  float avgRaw = totalRaw / 10.0;
  
  // Convert to Voltage: (Raw / 4095) * 3.3V
  zeroPointVoltage = (avgRaw / 4095.0) * 3.3;
  
  DEBUG_SERIAL.print(">>> Current Sensor Calibrated. Zero Point: ");
  DEBUG_SERIAL.print(zeroPointVoltage);
  DEBUG_SERIAL.println(" V <<<");
}

float readCurrent() {
  // 1. Read Raw ADC (0-4095)
  int rawValue = analogRead(CURRENT_PIN);
  
  // 2. Convert to Voltage (0-3.3V)
  float voltage = (rawValue / 4095.0) * 3.3;
  
  // 3. Calculate Difference from Zero Point
  // If voltage > zeroPoint, current is positive. 
  // If voltage < zeroPoint, current is negative (Regen braking/Charging).
  float difference = voltage - zeroPointVoltage;
  
  // 4. Convert Voltage to Amps
  // Amps = Voltage Difference / Sensitivity
  float amps = difference / sensitivity;
  // 5. Return Magnitude (Absolute Value)
  return abs(amps); 
}