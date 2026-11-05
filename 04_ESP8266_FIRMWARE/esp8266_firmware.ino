/*
 * ==============================================================================
 *  AI Autonomous Car: Standalone Single-File Arduino IDE Firmware (v2.0)
 * ==============================================================================
 *  Open this file directly in Arduino IDE for instant 1-click flashing!
 * ==============================================================================
 */

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <ESP8266WebServer.h>

// ------------------- PIN CONFIGURATION --------------------
#define PIN_PWMA  5   // D1 (GPIO 5)  - Left Motor Speed (PWM)
#define PIN_AIN1  4   // D2 (GPIO 4)  - Left Motor Dir 1
#define PIN_AIN2  0   // D3 (GPIO 0)  - Left Motor Dir 2
#define PIN_BIN1  14  // D5 (GPIO 14) - Right Motor Dir 1
#define PIN_BIN2  12  // D6 (GPIO 12) - Right Motor Dir 2
#define PIN_PWMB  13  // D7 (GPIO 13) - Right Motor Speed (PWM)
#define PIN_STBY  15  // D8 (GPIO 15) - TB6612 Standby Enable (Active HIGH)
#define PIN_LED   2   // D4 (GPIO 2)  - Onboard Status LED (LOW = ON)

// ------------------- WIFI ACCESS POINT --------------------
const char* AP_SSID     = "AutonomousCar_AP";
const char* AP_PASSWORD = "12345678";

WiFiUDP udp;
const unsigned int UDP_PORT = 8888;
char packetBuffer[256];

ESP8266WebServer server(80);

int currentTargetSpeed = 700;
int motorTrim = 0;
String currentAction = "STOP";
unsigned long lastHeartbeat = 0;
const unsigned long WATCHDOG_TIMEOUT_MS = 1000;

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
}

void stopCar() {
  analogWrite(PIN_PWMA, 0);
  analogWrite(PIN_PWMB, 0);
  digitalWrite(PIN_AIN1, LOW);
  digitalWrite(PIN_AIN2, LOW);
  digitalWrite(PIN_BIN1, LOW);
  digitalWrite(PIN_BIN2, LOW);
  currentAction = "STOP";
  digitalWrite(PIN_LED, HIGH);
}

void executeCommand(String action, int speed, int trim) {
  action.toUpperCase();
  lastHeartbeat = millis();
  motorTrim = constrain(trim, -100, 100);
  if (speed > 0) currentTargetSpeed = constrain(speed, 0, 1023);

  if (action == "FORWARD") {
    applyMotors(currentTargetSpeed, true, currentTargetSpeed, true);
    currentAction = "FORWARD";
    digitalWrite(PIN_LED, LOW);
  } else if (action == "BACKWARD") {
    applyMotors(currentTargetSpeed, false, currentTargetSpeed, false);
    currentAction = "BACKWARD";
  } else if (action == "LEFT") {
    applyMotors(currentTargetSpeed / 2, false, currentTargetSpeed, true);
    currentAction = "LEFT";
  } else if (action == "RIGHT") {
    applyMotors(currentTargetSpeed, true, currentTargetSpeed / 2, false);
    currentAction = "RIGHT";
  } else if (action == "STOP") {
    stopCar();
  }
}

void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(PIN_PWMA, OUTPUT);
  pinMode(PIN_AIN1, OUTPUT);
  pinMode(PIN_AIN2, OUTPUT);
  pinMode(PIN_BIN1, OUTPUT);
  pinMode(PIN_BIN2, OUTPUT);
  pinMode(PIN_PWMB, OUTPUT);
  pinMode(PIN_STBY, OUTPUT);
  pinMode(PIN_LED, OUTPUT);

  digitalWrite(PIN_STBY, HIGH);
  analogWriteFreq(1000);
  stopCar();

  // Create Standalone Access Point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.println("[WIFI] Access Point Started: " + String(AP_SSID));
  Serial.println("[WIFI] Car IP Address: " + WiFi.softAPIP().toString());

  udp.begin(UDP_PORT);
  Serial.printf("[UDP] Listening on Port %u\n", UDP_PORT);

  server.on("/ping", HTTP_GET, []() {
    server.send(200, "text/plain", "PONG | IP: " + WiFi.softAPIP().toString() + " | Uptime: " + String(millis()/1000) + "s");
  });
  server.begin();

  lastHeartbeat = millis();
}

void loop() {
  // UDP Command Receiver
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    int len = udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;
      String msg = String(packetBuffer);
      msg.trim();

      if (msg.startsWith("CMD:")) {
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

  server.handleClient();

  // Watchdog: Auto-stop if communication lost for >1.0s
  if (currentAction != "STOP" && (millis() - lastHeartbeat > WATCHDOG_TIMEOUT_MS)) {
    Serial.println("[WATCHDOG] Communication timeout. Halting vehicle.");
    stopCar();
  }
}
