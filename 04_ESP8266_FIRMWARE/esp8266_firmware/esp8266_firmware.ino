/*  
 * ==============================================================================
 *  AI Autonomous Car: Standalone Single-File Arduino IDE Firmware (v2.3 Universal)
 * ==============================================================================
 *  DUAL MODE: Cosmic Byte Ares Pro Manual Driving + Autonomous AI Vision
 *  UNIVERSAL HARDWARE PINOUT ENGINE (Includes Built-in Mobile Test & Diagnostics):
 *    - Profile A (Standard / Original Wiring):
 *        PWMA = D1 (GPIO 5), AIN1 = D2 (GPIO 4), AIN2 = D3 (GPIO 0)
 *        BIN1 = D5 (GPIO 14), BIN2 = D6 (GPIO 12), PWMB = D7 (GPIO 13)
 *        STBY = D8 (GPIO 15)
 *    - Profile B (Alternate Wiring):
 *        AIN1 = D1 (GPIO 5), AIN2 = D2 (GPIO 4), PWMA = D5 (GPIO 14)
 *        BIN1 = D7 (GPIO 13), BIN2 = D4 (GPIO 2), PWMB = D6 (GPIO 12)
 *        STBY = D0 (GPIO 16)
 *    - Failsafe: BOTH D8 AND D0 are always driven HIGH for Standby enable.
 * ==============================================================================
 */

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <ESP8266WebServer.h>
#include <EEPROM.h>

// ==================================================
// 1. PIN DEFINITIONS (NODE MCU GPIO ALIASES)
// ==================================================
#define PIN_D0  16 // GPIO 16 (WAKE / Profile B STBY)
#define PIN_D1  5  // GPIO 5  (Profile A PWMA / Profile B AIN1)
#define PIN_D2  4  // GPIO 4  (Profile A AIN1 / Profile B AIN2)
#define PIN_D3  0  // GPIO 0  (Profile A AIN2 / Flash)
#define PIN_D4  2  // GPIO 2  (Profile B BIN2 / Blue LED)
#define PIN_D5  14 // GPIO 14 (Profile A BIN1 / Profile B PWMA)
#define PIN_D6  12 // GPIO 12 (Profile A BIN2 / Profile B PWMB)
#define PIN_D7  13 // GPIO 13 (Profile A PWMB / Profile B BIN1)
#define PIN_D8  15 // GPIO 15 (Profile A STBY / Boot pulldown)

// Active Pinout Profile: 0 = Profile A (Standard/Original), 1 = Profile B (Alternate)
int activeProfile = 0; 
#define EEPROM_ADDR_PROFILE 0

// ==================================================
// 2. DUAL-WIFI CONFIGURATION (HOTSPOT + SOFT-AP)
// ==================================================
const char* STA_SSID     = "Kunal@Bsnl";
const char* STA_PASSWORD = "Kunal@646";

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
unsigned long totalPacketsReceived = 0;
String lastPacketMsg = "NONE";

// HTTP Movement Duration Tracker
bool httpMovementActive = false;
unsigned long httpStartTime = 0;
unsigned long httpDuration = 1000;

// ==================================================
// 4. LOW-LEVEL MOTOR HARDWARE ACTUATION
// ==================================================

void setStandbyHigh() {
  digitalWrite(PIN_D8, HIGH); // Standby for Profile A
  digitalWrite(PIN_D0, HIGH); // Standby for Profile B
}

void applyMotors(int leftSpeed, bool leftFwd, int rightSpeed, bool rightFwd) {
  int adjLeft = leftSpeed;
  int adjRight = rightSpeed;

  if (motorTrim < 0) adjLeft += (adjLeft * motorTrim / 200);
  else if (motorTrim > 0) adjRight -= (adjRight * motorTrim / 200);

  adjLeft = constrain(adjLeft, 0, 1023);
  adjRight = constrain(adjRight, 0, 1023);

  setStandbyHigh();

  if (activeProfile == 0) {
    // ---------------- PROFILE A (Standard / Original) ----------------
    // Left Motor (Motor A): PWMA = D1, AIN1 = D2, AIN2 = D3
    digitalWrite(PIN_D2, leftFwd ? HIGH : LOW);
    digitalWrite(PIN_D3, leftFwd ? LOW : HIGH);
    analogWrite(PIN_D1, adjLeft);

    // Right Motor (Motor B): BIN1 = D5, BIN2 = D6, PWMB = D7
    digitalWrite(PIN_D5, rightFwd ? HIGH : LOW);
    digitalWrite(PIN_D6, rightFwd ? LOW : HIGH);
    analogWrite(PIN_D7, adjRight);
  } else {
    // ---------------- PROFILE B (Alternate) --------------------------
    // Left Motor (Motor A): AIN1 = D1, AIN2 = D2, PWMA = D5
    digitalWrite(PIN_D1, leftFwd ? HIGH : LOW);
    digitalWrite(PIN_D2, leftFwd ? LOW : HIGH);
    analogWrite(PIN_D5, adjLeft);

    // Right Motor (Motor B): BIN1 = D7, BIN2 = D4, PWMB = D6
    digitalWrite(PIN_D7, rightFwd ? HIGH : LOW);
    digitalWrite(PIN_D4, rightFwd ? LOW : HIGH);
    analogWrite(PIN_D6, adjRight);
  }
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
  // Stop all PWM lines
  analogWrite(PIN_D1, 0);
  analogWrite(PIN_D5, 0);
  analogWrite(PIN_D6, 0);
  analogWrite(PIN_D7, 0);

  // Set direction lines low
  digitalWrite(PIN_D2, LOW);
  digitalWrite(PIN_D3, LOW);
  digitalWrite(PIN_D4, LOW);

  setStandbyHigh();

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
// 5. DIAGNOSTIC MOBILE WEB DASHBOARD (PORT 80)
// ==================================================

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<title>Autonomous Car Diagnostics</title>";
  html += "<style>";
  html += "body{background:#0F172A;color:#F8FAFC;font-family:sans-serif;margin:0;padding:16px;text-align:center;}";
  html += "h1{color:#38BDF8;font-size:22px;margin-bottom:4px;}";
  html += ".card{background:#1E293B;border:2px solid #334155;border-radius:12px;padding:14px;margin-bottom:14px;text-align:left;}";
  html += ".btn{display:block;width:100%;box-sizing:border-box;background:#0284C7;color:#fff;border:none;padding:14px;border-radius:8px;font-size:16px;font-weight:bold;margin:8px 0;cursor:pointer;text-decoration:none;text-align:center;}";
  html += ".btn-green{background:#16A34A;}.btn-red{background:#DC2626;}.btn-orange{background:#D97706;}.btn-purple{background:#9333EA;}";
  html += ".status-val{color:#4ADE80;font-weight:bold;}";
  html += ".badge{display:inline-block;padding:4px 8px;border-radius:6px;font-size:12px;font-weight:bold;background:#38BDF8;color:#000;}";
  html += "</style></head><body>";

  html += "<h1>🚗 AI CAR HARDWARE DASHBOARD</h1>";
  html += "<p style='color:#94A3B8;font-size:13px;margin-top:0;'>Firmware v2.3 Universal Engine</p>";

  // Profile Card
  html += "<div class='card'>";
  html += "<div><strong>Active Motor Pinout: </strong><span class='badge'>";
  html += (activeProfile == 0) ? "PROFILE A (Standard: D1,D2,D3,D5,D6,D7,D8)" : "PROFILE B (Alternate: D5,D1,D2,D6,D7,D4,D0)";
  html += "</span></div><br>";
  html += "<div>Current State: <span class='status-val'>" + currentAction + " (" + String(currentTargetSpeed) + " PWM)</span></div>";
  html += "<div>Last UDP Packet: <span class='status-val'>" + lastPacketMsg + "</span></div>";
  html += "<div>Total UDP Packets: <span class='status-val'>" + String(totalPacketsReceived) + "</span></div>";
  html += "<div>Uptime: <span class='status-val'>" + String(millis()/1000) + "s</span></div>";
  html += "</div>";

  // Motor Diagnostic Action Buttons
  html += "<div class='card'>";
  html += "<h3 style='margin-top:0;color:#FCD34D;'>⚡ 1-Tap Motor Spin Tests:</h3>";
  html += "<a href='/test_profile?p=0' class='btn btn-green'>▶ TEST PROFILE A (Standard 3s Forward)</a>";
  html += "<a href='/test_profile?p=1' class='btn btn-purple'>▶ TEST PROFILE B (Alternate 3s Forward)</a>";
  html += "<a href='/set_profile?p=0' class='btn btn-orange'>💾 SAVE PROFILE A AS PERMANENT DEFAULT</a>";
  html += "<a href='/set_profile?p=1' class='btn btn-orange'>💾 SAVE PROFILE B AS PERMANENT DEFAULT</a>";
  html += "<a href='/stop' class='btn btn-red'>🛑 EMERGENCY STOP MOTORS</a>";
  html += "</div>";

  // Battery Troubleshooting Checklist
  html += "<div class='card' style='font-size:13px;line-height:1.5;'>";
  html += "<h3 style='margin-top:0;color:#38BDF8;'>🔋 Agar Pahiya Abhi Bhi Na Ghume:</h3>";
  html += "<ol style='padding-left:18px;margin:0;'>";
  html += "<li><strong>Battery Switch:</strong> 18650 Battery holder se LM2596 `IN+` aur TB6612 `VM` ka switch <strong>ON</strong> hona chahiye.</li>";
  html += "<li><strong>VM Power Check:</strong> TB6612 ke `VM` pin par 7.4V milna zaroori hai (USB cable se sirf ESP chalta hai, motor nahi).</li>";
  html += "<li><strong>STBY Pin:</strong> TB6612 ka `STBY` pin HIGH hona chahiye. (Humne D8 aur D0 dono ko HIGH rakha hai).</li>";
  html += "<li><strong>Common Ground:</strong> Battery (-), NodeMCU GND, aur TB6612 GND aapas me jude hone chahiye.</li>";
  html += "</ol>";
  html += "</div>";

  html += "</body></html>";
  server.send(200, "text/html", html);
}

void handleTestProfile() {
  if (server.hasArg("p")) {
    activeProfile = server.arg("p").toInt();
  }
  executeCommand("FORWARD", 850, 0);
  httpMovementActive = true;
  httpStartTime = millis();
  httpDuration = 3000; // 3 seconds forward spin test
  lastHeartbeat = millis();

  server.sendHeader("Location", "/");
  server.send(303);
}

void handleSetProfile() {
  if (server.hasArg("p")) {
    activeProfile = server.arg("p").toInt();
    EEPROM.write(EEPROM_ADDR_PROFILE, activeProfile);
    EEPROM.commit();
  }
  server.sendHeader("Location", "/");
  server.send(303);
}

void handleStop() {
  stopCar();
  server.sendHeader("Location", "/");
  server.send(303);
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

  server.send(200, "text/plain", "ACK:" + cmd + ":RUNNING [Profile " + (activeProfile==0 ? "A" : "B") + "]");
}

// ==================================================
// 6. SETUP ROUTINE
// ==================================================

void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println("\n\n==============================================");
  Serial.println("  AI AUTONOMOUS CAR UNIVERSAL FIRMWARE v2.3   ");
  Serial.println("  SUPPORTING DUAL PINOUTS (A & B) + WEB DIAG  ");
  Serial.println("==============================================");

  // Initialize EEPROM and read saved profile
  EEPROM.begin(64);
  byte saved = EEPROM.read(EEPROM_ADDR_PROFILE);
  if (saved == 0 || saved == 1) {
    activeProfile = saved;
  } else {
    activeProfile = 0; // Default: Profile A (Standard)
  }
  Serial.printf("[CONFIG] Active Motor Pinout Profile: %s\n", activeProfile == 0 ? "A (Standard)" : "B (Alternate)");

  // Initialize all potential motor and standby pins as OUTPUT
  pinMode(PIN_D0, OUTPUT);
  pinMode(PIN_D1, OUTPUT);
  pinMode(PIN_D2, OUTPUT);
  pinMode(PIN_D3, OUTPUT);
  pinMode(PIN_D4, OUTPUT);
  pinMode(PIN_D5, OUTPUT);
  pinMode(PIN_D6, OUTPUT);
  pinMode(PIN_D7, OUTPUT);
  pinMode(PIN_D8, OUTPUT);

  analogWriteRange(1023);
  analogWriteFreq(1000);

  // Guarantee Standby is HIGH on both D8 and D0
  setStandbyHigh();
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

  // 4. Diagnostic Web Server Handlers
  server.on("/", HTTP_GET, handleRoot);
  server.on("/cmd", HTTP_GET, handleHttpCommand);
  server.on("/test_profile", HTTP_GET, handleTestProfile);
  server.on("/set_profile", HTTP_GET, handleSetProfile);
  server.on("/stop", HTTP_GET, handleStop);
  server.on("/ping", HTTP_GET, []() {
    server.send(200, "text/plain", "PONG | Profile: " + String(activeProfile == 0 ? "A" : "B") + " | Uptime: " + String(millis()/1000) + "s");
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
      totalPacketsReceived++;
      lastPacketMsg = msg;

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
