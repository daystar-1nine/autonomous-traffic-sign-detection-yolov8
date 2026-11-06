/*  
 * ==============================================================================
 *  AI Autonomous Car: Standalone Single-File Arduino IDE Firmware (v2.2)
 * ==============================================================================
 *  DUAL MODE: Cosmic Byte Ares Pro Manual Driving + Autonomous AI Vision
 *  CONFIGURED SPECIFICALLY FOR YOUR EXACT PHYSICAL WIRING:
 *    Motor A (Left) : AIN1 = D1, AIN2 = D2, PWMA = D5
 *    Motor B (Right): BIN1 = D7, BIN2 = D4, PWMB = D6
 *    Standby        : STBY = D0
 * ==============================================================================
 */

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <ESP8266WebServer.h>

// ==================================================
// 1. PIN CONFIGURATION (EXACT MATCH TO YOUR WIRING)
// ==================================================

// Motor A - Left
#define PIN_AIN1  5   // D1 (GPIO 5)  - Direction 1
#define PIN_AIN2  4   // D2 (GPIO 4)  - Direction 2
#define PIN_PWMA  14  // D5 (GPIO 14) - Speed (PWM)

// Motor B - Right
#define PIN_BIN1  13  // D7 (GPIO 13) - Direction 1
#define PIN_BIN2  2   // D4 (GPIO 2)  - Direction 2
#define PIN_PWMB  12  // D6 (GPIO 12) - Speed (PWM)

// Standby Pin
#define PIN_STBY  16  // D0 (GPIO 16) - Active HIGH

// ==================================================
// 2. DUAL-WIFI CONFIGURATION (HOTSPOT + SOFT-AP)
// ==================================================

// Phone Hotspot Credentials (from your working code)
const char* STA_SSID     = "Kunal@Bsnl";
const char* STA_PASSWORD = "Kunal@646";

// Standalone Fallback Access Point (Direct Car Hotspot)
const char* AP_SSID      = "AutonomousCar_AP";
const char* AP_PASSWORD  = "car12345678";

WiFiUDP udp;
const unsigned int UDP_PORT = 8888;
char packetBuffer[256];

ESP8266WebServer server(80);

// ==================================================
// 3. MOTOR SPEED & STATE VARIABLES
// ==================================================

int currentTargetSpeed = 700;
int motorTrim = 0;
String currentAction = "STOP";
unsigned long lastHeartbeat = 0;
const unsigned long WATCHDOG_TIMEOUT_MS = 1000;

// HTTP Movement Duration Tracker
bool httpMovementActive = false;
unsigned long httpStartTime = 0;
unsigned long httpDuration = 1000;

// ==================================================
// 4. LOW-LEVEL MOTOR HARDWARE ACTUATION
// ==================================================

void applyMotors(int leftSpeed, bool leftFwd, int rightSpeed, bool rightFwd) {
  int adjLeft = leftSpeed;
  int adjRight = rightSpeed;

  if (motorTrim < 0) adjLeft += (adjLeft * motorTrim / 200);
  else if (motorTrim > 0) adjRight -= (adjRight * motorTrim / 200);

  adjLeft = constrain(adjLeft, 0, 1023);
  adjRight = constrain(adjRight, 0, 1023);

  digitalWrite(PIN_AIN1, leftFwd ? HIGH : LOW);
  digitalWrite(PIN_AIN2, leftFwd ? LOW : HIGH);
  analogWrite(PIN_PWMA, adjLeft);

  digitalWrite(PIN_BIN1, rightFwd ? HIGH : LOW);
  digitalWrite(PIN_BIN2, rightFwd ? LOW : HIGH);
  analogWrite(PIN_PWMB, adjRight);

  digitalWrite(PIN_STBY, HIGH);
}

void driveDirect(int leftPwm, int rightPwm) {
  int lPwm = constrain(leftPwm, -1023, 1023);
  int rPwm = constrain(rightPwm, -1023, 1023);

  bool leftFwd = (lPwm >= 0);
  bool rightFwd = (rPwm >= 0);

  applyMotors(abs(lPwm), leftFwd, abs(rPwm), rightFwd);
  currentAction = "DRIVE";
  currentTargetSpeed = max(abs(lPwm), abs(rPwm));
}

void stopCar() {
  analogWrite(PIN_PWMA, 0);
  analogWrite(PIN_PWMB, 0);
  digitalWrite(PIN_AIN1, LOW);
  digitalWrite(PIN_AIN2, LOW);
  digitalWrite(PIN_BIN1, LOW);
  digitalWrite(PIN_BIN2, LOW);
  digitalWrite(PIN_STBY, HIGH);

  currentAction = "STOP";
  currentTargetSpeed = 0;
  httpMovementActive = false;
}

void executeCommand(String action, int speed, int trim) {
  motorTrim = constrain(trim, -100, 100);
  currentTargetSpeed = constrain(speed, 0, 1023);

  if (action == "FORWARD") {
    applyMotors(currentTargetSpeed, true, currentTargetSpeed, true);
    currentAction = "FORWARD";
  } else if (action == "BACKWARD") {
    applyMotors(currentTargetSpeed, false, currentTargetSpeed, false);
    currentAction = "BACKWARD";
  } else if (action == "LEFT") {
    // Sharp differential pivot turn: Left reverse, Right forward
    applyMotors(currentTargetSpeed, false, currentTargetSpeed, true);
    currentAction = "LEFT";
  } else if (action == "RIGHT") {
    // Sharp differential pivot turn: Left forward, Right reverse
    applyMotors(currentTargetSpeed, true, currentTargetSpeed, false);
    currentAction = "RIGHT";
  } else if (action == "STOP") {
    stopCar();
  }
}

// ==================================================
// 5. HTTP WEB SERVER HANDLERS (BACKWARD COMPATIBLE)
// ==================================================

void handleRoot() {
  String msg = "AUTONOMOUS CAR ONLINE (DUAL-MODE v2.2)\n";
  msg += "STA IP (Hotspot): " + (WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString() : "DISCONNECTED") + "\n";
  msg += "SoftAP IP: " + WiFi.softAPIP().toString() + "\n";
  msg += "Current Command: " + currentAction + "\n";
  msg += "Motor Speed: " + String(currentTargetSpeed) + "\n";
  msg += "Uptime: " + String(millis() / 1000) + "s\n";
  server.send(200, "text/plain", msg);
}

void handleHttpCommand() {
  lastHeartbeat = millis();

  if (!server.hasArg("value")) {
    server.send(400, "text/plain", "ERROR: Missing value argument");
    return;
  }

  String cmd = server.arg("value");
  cmd.trim();
  cmd.toUpperCase();

  unsigned long duration = 1000;
  if (server.hasArg("duration")) {
    duration = server.arg("duration").toInt();
    if (duration < 100) duration = 100;
    if (duration > 10000) duration = 10000;
  }

  if (cmd == "STOP") {
    stopCar();
    server.send(200, "text/plain", "ACK:STOP");
    return;
  }

  int speed = 700;
  if (server.hasArg("speed")) {
    speed = server.arg("speed").toInt();
  }

  executeCommand(cmd, speed, motorTrim);
  httpMovementActive = true;
  httpStartTime = millis();
  httpDuration = duration;

  server.send(200, "text/plain", "ACK:" + cmd + ":RUNNING");
}

// ==================================================
// 6. SETUP ROUTINE
// ==================================================

void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println("\n\n==============================================");
  Serial.println("  AI AUTONOMOUS CAR DUAL-MODE FIRMWARE v2.2   ");
  Serial.println("  CONFIGURED FOR YOUR PHYSICAL HARDWARE PINS  ");
  Serial.println("==============================================");

  pinMode(PIN_AIN1, OUTPUT);
  pinMode(PIN_AIN2, OUTPUT);
  pinMode(PIN_PWMA, OUTPUT);

  pinMode(PIN_BIN1, OUTPUT);
  pinMode(PIN_BIN2, OUTPUT);
  pinMode(PIN_PWMB, OUTPUT);

  pinMode(PIN_STBY, OUTPUT);

  analogWriteRange(1023);
  analogWriteFreq(1000);

  digitalWrite(PIN_STBY, HIGH);
  stopCar();

  // Dual Wi-Fi Mode: Both Station (Phone Hotspot) AND SoftAP (Direct)
  WiFi.mode(WIFI_AP_STA);

  // 1. Start SoftAP
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.println("[WIFI] SoftAP Active: " + String(AP_SSID));
  Serial.println("[WIFI] AP IP: " + WiFi.softAPIP().toString());

  // 2. Connect to Phone Hotspot
  WiFi.begin(STA_SSID, STA_PASSWORD);
  Serial.print("[WIFI] Connecting to Phone Hotspot: " + String(STA_SSID));
  unsigned long startAttempt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 8000) {
    delay(400);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("[WIFI] HOTSPOT CONNECTED!");
    Serial.println("[WIFI] Hotspot IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("[WIFI] Hotspot not found. Accessible via SoftAP at 192.168.4.1");
  }

  // 3. UDP Receiver (Port 8888 for low-latency Gamepad & Vision AI)
  udp.begin(UDP_PORT);
  Serial.printf("[UDP] Listening on Port %u\n", UDP_PORT);

  // 4. HTTP Web Server Handlers
  server.on("/", HTTP_GET, handleRoot);
  server.on("/cmd", HTTP_GET, handleHttpCommand);
  server.on("/ping", HTTP_GET, []() {
    server.send(200, "text/plain", "PONG | Uptime: " + String(millis()/1000) + "s");
  });
  server.begin();
  Serial.println("[HTTP] Web Server Started on Port 80");

  lastHeartbeat = millis();
}

// ==================================================
// 7. MAIN EXECUTION LOOP
// ==================================================

void loop() {
  server.handleClient();

  // UDP High-Speed Command Receiver (Gamepad & AI)
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    int len = udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;
      String msg = String(packetBuffer);
      msg.trim();
      lastHeartbeat = millis();

      // Direct Drive Mode: "CMD:DRIVE:<LEFT>:<RIGHT>:<SEQ>"
      if (msg.startsWith("CMD:DRIVE:")) {
        int p1 = 10;
        int p2 = msg.indexOf(':', p1);
        int p3 = (p2 > 0) ? msg.indexOf(':', p2 + 1) : -1;
        int leftPwm = (p2 > 0) ? msg.substring(p1, p2).toInt() : 0;
        int rightPwm = (p2 > 0 && p3 > 0) ? msg.substring(p2 + 1, p3).toInt() : (p2 > 0 ? msg.substring(p2 + 1).toInt() : 0);

        driveDirect(leftPwm, rightPwm);

        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.print("ACK:DRIVE");
        udp.endPacket();
      }
      // Action Mode: "CMD:<ACTION>:<SPEED>:<TRIM>:<SEQ>"
      else if (msg.startsWith("CMD:")) {
        int p1 = msg.indexOf(':', 4);
        int p2 = (p1 > 0) ? msg.indexOf(':', p1 + 1) : -1;
        String act = (p1 > 0) ? msg.substring(4, p1) : msg.substring(4);
        int spd = (p1 > 0 && p2 > 0) ? msg.substring(p1 + 1, p2).toInt() : 700;
        int trm = (p2 > 0) ? msg.substring(p2 + 1).toInt() : 0;

        executeCommand(act, spd, trm);

        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.print("ACK:" + currentAction);
        udp.endPacket();
      }
    }
  }

  // HTTP Duration Auto-Timeout
  if (httpMovementActive && millis() - httpStartTime >= httpDuration) {
    stopCar();
  }

  // Hardware Safety Watchdog: Auto-Stop if communication lost for >1.0s
  if (currentAction != "STOP" && (millis() - lastHeartbeat > WATCHDOG_TIMEOUT_MS)) {
    Serial.println("[WATCHDOG] Communication timeout! Emergency auto-stop.");
    stopCar();
  }
}