/*
 * ==============================================================================
 *  AI Autonomous Car: Unified Complete Firmware (Dual-Mode: UDP + HTTP)
 * ==============================================================================
 *  - TB6612FNG MOTOR LOGIC: Exactly matching your working motor test pins & functions
 *  - HIGH-SPEED UDP (Port 8888): Real-time AI Vision + Cosmic Byte Gamepad Control
 *  - HTTP WEB SERVER (Port 80): Preserves /cmd?value=... and / diagnostic page
 *  - DUAL WI-FI: Phone Hotspot ("Kunal@Bsnl") + Standalone SoftAP ("AutonomousCar_AP")
 * ==============================================================================
 */

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <ESP8266WebServer.h>

// ==================================================
// 1. PIN CONFIGURATION (EXACT MATCH TO YOUR WORKING TEST)
// ==================================================

// Motor A - Left
#define AIN1 D1
#define AIN2 D2
#define PWMA D5

// Motor B - Right
#define BIN1 D7
#define BIN2 D4
#define PWMB D6

#define STBY D0

// ==================================================
// 2. WI-FI CREDENTIALS & PROTOCOLS
// ==================================================

const char* WIFI_SSID     = "Kunal@Bsnl";
const char* WIFI_PASSWORD = "Kunal@646";

// Fallback SoftAP if Hotspot is off
const char* AP_SSID       = "AutonomousCar_AP";
const char* AP_PASSWORD   = "car12345678";

ESP8266WebServer server(80);
WiFiUDP udp;
const unsigned int UDP_PORT = 8888;
char packetBuffer[256];

// ==================================================
// 3. MOTOR SPEED & STATE VARIABLES
// ==================================================

int currentMotorSpeed = 700; // Autonomous default (400-1023)
int motorTrim = 0;           // Steering trim offset (-100 to +100)
String currentCommand = "STOP";

// Movement Duration & Watchdog Tracker
bool movementActive = false;
unsigned long movementStartTime = 0;
unsigned long movementDuration = 1000;
const unsigned long UDP_WATCHDOG_TIMEOUT_MS = 1000;
unsigned long lastHeartbeat = 0;
bool isUdpActive = false;

// ==================================================
// 4. LOW-LEVEL MOTOR PRIMITIVES
// ==================================================

void stopAllMotors() {
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);

  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);

  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, LOW);

  // Keep driver enabled
  digitalWrite(STBY, HIGH);
}

void setMotorA(int speed, bool forward) {
  int adjSpeed = speed;
  if (motorTrim < 0) adjSpeed += (adjSpeed * motorTrim / 200);
  adjSpeed = constrain(adjSpeed, 0, 1023);

  digitalWrite(AIN1, forward ? HIGH : LOW);
  digitalWrite(AIN2, forward ? LOW : HIGH);
  analogWrite(PWMA, adjSpeed);
}

void setMotorB(int speed, bool forward) {
  int adjSpeed = speed;
  if (motorTrim > 0) adjSpeed -= (adjSpeed * motorTrim / 200);
  adjSpeed = constrain(adjSpeed, 0, 1023);

  digitalWrite(BIN1, forward ? HIGH : LOW);
  digitalWrite(BIN2, forward ? LOW : HIGH);
  analogWrite(PWMB, adjSpeed);
}

// ==================================================
// 5. MOTOR CONTROL FUNCTIONS (YOUR WORKING TEST FUNCTIONS)
// ==================================================

void motorAForward() {
  setMotorA(currentMotorSpeed, true);
}

void motorABackward() {
  setMotorA(currentMotorSpeed, false);
}

void motorBForward() {
  setMotorB(currentMotorSpeed, true);
}

void motorBBackward() {
  setMotorB(currentMotorSpeed, false);
}

void bothForward() {
  motorAForward();
  motorBForward();
}

void bothBackward() {
  motorABackward();
  motorBBackward();
}

// ==================================================
// 6. HIGH-LEVEL MOVEMENT FUNCTIONS
// ==================================================

void moveForward() {
  digitalWrite(STBY, HIGH);
  bothForward();
  currentCommand = "FORWARD";
  Serial.println("MOVING FORWARD");
}

void moveBackward() {
  digitalWrite(STBY, HIGH);
  bothBackward();
  currentCommand = "BACKWARD";
  Serial.println("MOVING BACKWARD");
}

void turnLeft() {
  digitalWrite(STBY, HIGH);
  motorABackward();
  motorBForward();
  currentCommand = "LEFT";
  Serial.println("TURNING LEFT");
}

void turnRight() {
  digitalWrite(STBY, HIGH);
  motorAForward();
  motorBBackward();
  currentCommand = "RIGHT";
  Serial.println("TURNING RIGHT");
}

void stopCar() {
  stopAllMotors();
  movementActive = false;
  isUdpActive = false;
  currentCommand = "STOP";
  Serial.println("CAR STOPPED");
}

// Direct Differential Drive (Cosmic Byte Ares Pro Gamepad)
void driveDirect(int leftPwm, int rightPwm) {
  digitalWrite(STBY, HIGH);

  bool leftFwd = (leftPwm >= 0);
  bool rightFwd = (rightPwm >= 0);

  setMotorA(abs(leftPwm), leftFwd);
  setMotorB(abs(rightPwm), rightFwd);

  currentCommand = "DRIVE";
  currentMotorSpeed = max(abs(leftPwm), abs(rightPwm));
  isUdpActive = true;
  lastHeartbeat = millis();
}

// ==================================================
// 7. COMMAND EXECUTION (HTTP & UDP UNIFIED)
// ==================================================

bool isValidCommand(String command) {
  return (
    command == "FORWARD" ||
    command == "BACKWARD" ||
    command == "LEFT" ||
    command == "RIGHT" ||
    command == "STOP"
  );
}

void executeCommand(String command, unsigned long duration, int speed = -1, int trim = 0) {
  if (speed > 0) currentMotorSpeed = constrain(speed, 0, 1023);
  motorTrim = constrain(trim, -100, 100);

  if (command == "STOP") {
    stopCar();
    return;
  }

  movementStartTime = millis();
  movementDuration = duration;
  movementActive = true;

  if (command == "FORWARD") {
    moveForward();
  } else if (command == "BACKWARD") {
    moveBackward();
  } else if (command == "LEFT") {
    turnLeft();
  } else if (command == "RIGHT") {
    turnRight();
  }
}

// ==================================================
// 8. HTTP WEB SERVER HANDLERS (PRESERVES WORKING LOGIC)
// ==================================================

void handleRoot() {
  String message = "AUTONOMOUS CAR ONLINE (DUAL-MODE UDP+HTTP)\n";
  message += "STA IP (Hotspot): " + (WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString() : "DISCONNECTED") + "\n";
  message += "SoftAP IP: " + WiFi.softAPIP().toString() + "\n";
  message += "UDP Port: " + String(UDP_PORT) + " (Active for AI App & Gamepad)\n";
  message += "Current Command: " + currentCommand + "\n";
  message += "Motor Speed: " + String(currentMotorSpeed) + "\n";
  message += "Uptime: " + String(millis() / 1000) + "s\n\n";
  message += "Available HTTP Commands (/cmd?value=<CMD>&duration=<MS>):\n";
  message += "• FORWARD\n• BACKWARD\n• LEFT\n• RIGHT\n• STOP\n";
  server.send(200, "text/plain", message);
}

void handleCommand() {
  if (!server.hasArg("value")) {
    server.send(400, "text/plain", "ERROR: Missing command");
    return;
  }

  String command = server.arg("value");
  command.trim();
  command.toUpperCase();

  if (!isValidCommand(command)) {
    server.send(400, "text/plain", "ERROR: Invalid command");
    return;
  }

  if (command == "STOP") {
    executeCommand("STOP", 0);
    server.send(200, "text/plain", "ACK:STOP");
    return;
  }

  unsigned long duration = 1000;
  if (server.hasArg("duration")) {
    duration = server.arg("duration").toInt();
    if (duration < 100) duration = 100;
    if (duration > 10000) duration = 10000;
  }

  executeCommand(command, duration);
  server.send(200, "text/plain", "ACK:" + command + ":RUNNING");
}

// ==================================================
// 9. UDP PACKET DISPATCHER (ANDROID AI APP & GAMEPAD)
// ==================================================

void processUdpPackets() {
  int packetSize = udp.parsePacket();
  if (!packetSize) return;

  int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
  if (len > 0) {
    packetBuffer[len] = '\0';
    String msg = String(packetBuffer);
    msg.trim();
    lastHeartbeat = millis();

    // 1. Gamepad Direct Drive: "CMD:DRIVE:<LEFT>:<RIGHT>:<SEQ>"
    if (msg.startsWith("CMD:DRIVE:")) {
      int firstColon = msg.indexOf(':', 10);
      int secondColon = (firstColon != -1) ? msg.indexOf(':', firstColon + 1) : -1;

      if (firstColon != -1) {
        int leftPwm = msg.substring(10, firstColon).toInt();
        int rightPwm = (secondColon != -1) ? msg.substring(firstColon + 1, secondColon).toInt() : msg.substring(firstColon + 1).toInt();
        driveDirect(leftPwm, rightPwm);
      }
    }
    // 2. Autonomous Action: "CMD:<ACTION>:<SPEED>:<TRIM>:<SEQ>"
    else if (msg.startsWith("CMD:")) {
      int idx1 = msg.indexOf(':', 4);
      String action;
      int speed = 700;
      int trim = 0;

      if (idx1 != -1) {
        action = msg.substring(4, idx1);
        int idx2 = msg.indexOf(':', idx1 + 1);
        if (idx2 != -1) {
          speed = msg.substring(idx1 + 1, idx2).toInt();
          int idx3 = msg.indexOf(':', idx2 + 1);
          if (idx3 != -1) {
            trim = msg.substring(idx2 + 1, idx3).toInt();
          } else {
            trim = msg.substring(idx2 + 1).toInt();
          }
        } else {
          speed = msg.substring(idx1 + 1).toInt();
        }
      } else {
        action = msg.substring(4);
      }

      action.toUpperCase();
      isUdpActive = true;
      executeCommand(action, 0, speed, trim); // duration 0 = continuous until next packet or watchdog
    }

    // Send ACK response back so Android HUD displays active ping
    udp.beginPacket(udp.remoteIP(), udp.remotePort());
    String reply = "ACK:" + currentCommand + ":" + String(currentMotorSpeed) + ":" + String(millis());
    udp.write(reply.c_str());
    udp.endPacket();
  }
}

// ==================================================
// 10. SETUP & INITIALIZATION
// ==================================================

void setup() {
  Serial.begin(115200);

  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);

  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  pinMode(STBY, OUTPUT);

  analogWriteRange(1023);
  analogWriteFreq(1000);

  // Initialize driver exactly like working test
  digitalWrite(STBY, LOW);
  stopAllMotors();

  Serial.println();
  Serial.println("==============================================");
  Serial.println("  AUTONOMOUS CAR UNIFIED FIRMWARE INITIALIZING");
  Serial.println("  TB6612FNG: D1, D2, D5 | D7, D4, D6 | STBY D0 ");
  Serial.println("==============================================");

  // Enable driver
  digitalWrite(STBY, HIGH);

  // Dual Wi-Fi Mode: Station (Hotspot) + SoftAP Fallback
  WiFi.mode(WIFI_AP_STA);
  WiFi.persistent(false);
  WiFi.setAutoReconnect(true);

  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.print("[AP] SoftAP IP: ");
  Serial.println(WiFi.softAPIP());

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to phone hotspot (");
  Serial.print(WIFI_SSID);
  Serial.print(")");

  unsigned long startWifi = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - startWifi < 10000)) {
    delay(400);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WIFI CONNECTED TO HOTSPOT!");
    Serial.print("ESP IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("HOTSPOT NOT FOUND -> RUNNING ON SoftAP (AutonomousCar_AP / 192.168.4.1)");
  }

  // Start HTTP Server
  server.on("/", HTTP_GET, handleRoot);
  server.on("/cmd", HTTP_GET, handleCommand);
  server.onNotFound([]() {
    server.send(404, "text/plain", "ENDPOINT NOT FOUND");
  });
  server.begin();
  Serial.println("HTTP SERVER STARTED ON PORT 80");

  // Start UDP Server
  udp.begin(UDP_PORT);
  Serial.printf("UDP SERVER LISTENING ON PORT %u\n", UDP_PORT);
  Serial.println("SYSTEM READY FOR ANDROID APP & GAMEPAD");
}

// ==================================================
// 11. MAIN LOOP
// ==================================================

void loop() {
  server.handleClient();
  processUdpPackets();

  unsigned long now = millis();

  // 1. HTTP timed movement timeout (e.g. 1000ms from browser test)
  if (movementActive && !isUdpActive && (now - movementStartTime >= movementDuration)) {
    Serial.println("HTTP MOVEMENT TIMEOUT");
    stopCar();
  }

  // 2. UDP Watchdog Failsafe (If UDP packet stream stops for >1000ms, safely stop car)
  if (isUdpActive && (now - lastHeartbeat > UDP_WATCHDOG_TIMEOUT_MS)) {
    Serial.println("UDP WATCHDOG TIMEOUT -> MOTORS HALTED");
    stopCar();
  }

  // 3. Wi-Fi Disconnect Safety
  if (WiFi.status() != WL_CONNECTED && WiFi.softAPgetStationNum() == 0 && (movementActive || isUdpActive)) {
    Serial.println("WIFI DISCONNECTED -> MOTORS HALTED");
    stopCar();
  }
}
