/*
 * ==============================================================================
 *  AI-Based Autonomous Car: NodeMCU ESP8266 + TB6612FNG Firmware
 * ==============================================================================
 *  Receives real-time navigation commands from Python YOLOv8 Computer Vision Brain
 *  via high-speed HTTP REST API / WiFi.
 *
 *  Hardware Connections (NodeMCU -> TB6612FNG):
 *  - D1 (GPIO 5)  -> PWMA (Left Motor Speed)
 *  - D2 (GPIO 4)  -> AIN1 (Left Motor Dir 1)
 *  - D3 (GPIO 0)  -> AIN2 (Left Motor Dir 2)
 *  - D5 (GPIO 14) -> BIN1 (Right Motor Dir 1)
 *  - D6 (GPIO 12) -> BIN2 (Right Motor Dir 2)
 *  - D7 (GPIO 13) -> PWMB (Right Motor Speed)
 *  - D8 (GPIO 15) -> STBY (Driver Standby Enable - Active HIGH)
 *  - VIN          -> 5.0V from Buck Converter
 *  - GND          -> Common Ground with Battery & TB6612FNG
 * ==============================================================================
 */

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// ---------------------- PIN DEFINITIONS ----------------------
#define PIN_PWMA  5   // D1 - Left Motor Speed (PWM 0-1023)
#define PIN_AIN1  4   // D2 - Left Motor Direction 1
#define PIN_AIN2  0   // D3 - Left Motor Direction 2

#define PIN_BIN1  14  // D5 - Right Motor Direction 1
#define PIN_BIN2  12  // D6 - Right Motor Direction 2
#define PIN_PWMB  13  // D7 - Right Motor Speed (PWM 0-1023)

#define PIN_STBY  15  // D8 - Motor Driver Standby Enable
#define PIN_LED   2   // D4 - Onboard Status LED (Inverted: LOW = ON)

// ---------------------- WIFI CONFIGURATION --------------------
// Set to 1 to connect to an existing WiFi Hotspot (e.g. Phone/Home),
// or set to 0 to create Car's own independent Hotspot (No router needed!).
#define USE_STATION_MODE 1

const char* STA_SSID     = "Your_Hotspot_SSID";    // Change to your phone hotspot name
const char* STA_PASSWORD = "Your_Hotspot_Password";// Change to your hotspot password

const char* AP_SSID      = "AutonomousCar_AP";     // Car Access Point SSID
const char* AP_PASSWORD  = "12345678";             // Car Access Point Password

// ---------------------- SPEED & TIMING TUNING -----------------
const int DEFAULT_CRUISE_SPEED = 700; // Normal forward speed (0-1023)
const int SLOW_CRUISE_SPEED    = 450; // Speed Limit / Approach speed
const int TURN_SPEED           = 750; // Turning speed
const int MAX_SPEED            = 950; // High speed

int currentSpeed = DEFAULT_CRUISE_SPEED;
String currentCommand = "STOP";
unsigned long lastCommandTime = 0;
const unsigned long WATCHDOG_TIMEOUT_MS = 1200; // Auto-stop if no command received for 1.2s

// ---------------------- WEB SERVER INSTANCE -------------------
ESP8266WebServer server(80);

// ---------------------- MOTOR DRIVER FUNCTIONS ----------------
void initMotors() {
  pinMode(PIN_PWMA, OUTPUT);
  pinMode(PIN_AIN1, OUTPUT);
  pinMode(PIN_AIN2, OUTPUT);
  pinMode(PIN_BIN1, OUTPUT);
  pinMode(PIN_BIN2, OUTPUT);
  pinMode(PIN_PWMB, OUTPUT);
  pinMode(PIN_STBY, OUTPUT);
  pinMode(PIN_LED, OUTPUT);

  // Enable Motor Driver (STBY must be HIGH)
  digitalWrite(PIN_STBY, HIGH);
  stopMotors();
}

void setLeftMotor(int speed, bool forward) {
  speed = constrain(speed, 0, 1023);
  if (forward) {
    digitalWrite(PIN_AIN1, HIGH);
    digitalWrite(PIN_AIN2, LOW);
  } else {
    digitalWrite(PIN_AIN1, LOW);
    digitalWrite(PIN_AIN2, HIGH);
  }
  analogWrite(PIN_PWMA, speed);
}

void setRightMotor(int speed, bool forward) {
  speed = constrain(speed, 0, 1023);
  if (forward) {
    digitalWrite(PIN_BIN1, HIGH);
    digitalWrite(PIN_BIN2, LOW);
  } else {
    digitalWrite(PIN_BIN1, LOW);
    digitalWrite(PIN_BIN2, HIGH);
  }
  analogWrite(PIN_PWMB, speed);
}

void stopMotors() {
  analogWrite(PIN_PWMA, 0);
  analogWrite(PIN_PWMB, 0);
  digitalWrite(PIN_AIN1, LOW);
  digitalWrite(PIN_AIN2, LOW);
  digitalWrite(PIN_BIN1, LOW);
  digitalWrite(PIN_BIN2, LOW);
  currentCommand = "STOP";
  digitalWrite(PIN_LED, HIGH); // Turn LED off
}

void moveForward(int speed) {
  setLeftMotor(speed, true);
  setRightMotor(speed, true);
  currentCommand = "FORWARD";
  digitalWrite(PIN_LED, LOW); // LED ON
}

void moveBackward(int speed) {
  setLeftMotor(speed, false);
  setRightMotor(speed, false);
  currentCommand = "BACKWARD";
}

void turnLeft(int speed) {
  // Skid steering: Left wheel backwards, Right wheel forwards
  setLeftMotor(speed / 2, false);
  setRightMotor(speed, true);
  currentCommand = "LEFT";
}

void turnRight(int speed) {
  // Skid steering: Left wheel forwards, Right wheel backwards
  setLeftMotor(speed, true);
  setRightMotor(speed / 2, false);
  currentCommand = "RIGHT";
}

// ---------------------- HTTP REQUEST HANDLERS -----------------
void handleCarCommand() {
  if (server.hasArg("cmd")) {
    String cmd = server.arg("cmd");
    cmd.toUpperCase();

    // Check optional speed argument
    if (server.hasArg("speed")) {
      int s = server.arg("speed").toInt();
      if (s > 0 && s <= 1023) {
        currentSpeed = s;
      }
    }

    lastCommandTime = millis(); // Refresh watchdog timer

    if (cmd == "FORWARD") {
      moveForward(currentSpeed);
    } else if (cmd == "BACKWARD") {
      moveBackward(currentSpeed);
    } else if (cmd == "LEFT") {
      turnLeft(TURN_SPEED);
    } else if (cmd == "RIGHT") {
      turnRight(TURN_SPEED);
    } else if (cmd == "STOP") {
      stopMotors();
    } else if (cmd == "SPEED_LIMIT" || cmd == "SLOW") {
      currentSpeed = SLOW_CRUISE_SPEED;
      moveForward(currentSpeed);
    } else if (cmd == "SPEED_FAST" || cmd == "FAST") {
      currentSpeed = MAX_SPEED;
      moveForward(currentSpeed);
    } else if (cmd == "CRUISE") {
      currentSpeed = DEFAULT_CRUISE_SPEED;
      moveForward(currentSpeed);
    } else {
      server.send(400, "text/plain", "ERROR: Unknown command " + cmd);
      return;
    }

    String response = "OK: " + currentCommand + " | Speed: " + String(currentSpeed);
    server.send(200, "text/plain", response);
    Serial.println("[EXEC] " + response);
  } else {
    server.send(400, "text/plain", "ERROR: Missing 'cmd' parameter");
  }
}

void handlePing() {
  String info = "PONG | Status: OK | IP: " + WiFi.localIP().toString() +
                " | RSSI: " + String(WiFi.RSSI()) + " dBm | Uptime: " + String(millis() / 1000) + "s";
  server.send(200, "text/plain", info);
}

void handleStatus() {
  String json = "{";
  json += "\"command\":\"" + currentCommand + "\",";
  json += "\"speed\":" + String(currentSpeed) + ",";
  json += "\"uptime_s\":" + String(millis() / 1000) + ",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\"";
  json += "}";
  server.send(200, "application/json", json);
}

// ---------------------- ARDUINO SETUP & LOOP ------------------
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n\n========================================");
  Serial.println("  AI Autonomous Car ESP8266 Firmware    ");
  Serial.println("========================================");

  initMotors();

#if USE_STATION_MODE
  Serial.print("[WiFi] Connecting to: ");
  Serial.println(STA_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(STA_SSID, STA_PASSWORD);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 25) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected successfully!");
    Serial.print("[WiFi] IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WARN] Failed to connect to WiFi! Falling back to SoftAP mode...");
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASSWORD);
    Serial.print("[AP] Access Point started: ");
    Serial.println(AP_SSID);
    Serial.print("[AP] AP IP Address: ");
    Serial.println(WiFi.softAPIP());
  }
#else
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.print("[AP] Access Point started: ");
  Serial.println(AP_SSID);
  Serial.print("[AP] AP IP Address: ");
  Serial.println(WiFi.softAPIP());
#endif

  // Register Web Routes
  server.on("/car", HTTP_GET, handleCarCommand);
  server.on("/ping", HTTP_GET, handlePing);
  server.on("/status", HTTP_GET, handleStatus);

  server.begin();
  Serial.println("[HTTP] REST API Server started on port 80");
  Serial.println("[READY] Waiting for YOLOv8 Vision Brain commands...");
  lastCommandTime = millis();
}

void loop() {
  server.handleClient();

  // Watchdog Safety Check: If car is moving and no command has arrived for 1.2s, STOP!
  if (currentCommand != "STOP" && (millis() - lastCommandTime > WATCHDOG_TIMEOUT_MS)) {
    Serial.println("[WATCHDOG] Connection heartbeat lost! Auto-stopping motors for safety.");
    stopMotors();
  }
}
