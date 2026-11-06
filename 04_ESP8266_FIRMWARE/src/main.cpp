/**
 * @file main.cpp
 * @brief Autonomous AI Traffic Sign Car - Production ESP8266 Dual-Mode Firmware
 * @version 2.1.0 (Manual Ares Pro + Autonomous AI Vision Dual-Mode)
 */

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include "pin_config.h"
#include "motor_driver.h"
#include "udp_protocol.h"
#include "watchdog.h"

// ------------------- WIFI CONFIGURATION -------------------
// 0 = SoftAP Mode (Car creates its own hotspot: 192.168.4.1)
// 1 = Station Mode (Car connects to Android phone hotspot)
#define USE_STATION_MODE 0

const char* AP_SSID      = "AutonomousCar_AP";
const char* AP_PASSWORD  = "12345678";

const char* STA_SSID     = "RedmiHotspot";
const char* STA_PASSWORD = "carpassword123";

// ------------------- OBJECT INSTANCES ---------------------
MotorDriver motors;
UdpController udpServer(8888);
SafetyWatchdog watchdog(1000); // 1.0s timeout
ESP8266WebServer httpServer(80);

// ------------------- HTTP DIAGNOSTIC HANDLERS -------------
void handleHttpPing() {
    String resp = "PONG | Mode: " + String(USE_STATION_MODE ? "STA" : "AP") +
                  " | IP: " + (USE_STATION_MODE ? WiFi.localIP().toString() : WiFi.softAPIP().toString()) +
                  " | RSSI: " + String(WiFi.RSSI()) + " dBm | Uptime: " + String(millis() / 1000) + "s";
    httpServer.send(200, "text/plain", resp);
}

void handleHttpStatus() {
    String json = "{";
    json += "\"action\":\"" + motors.currentAction + "\",";
    json += "\"speed\":" + String(motors.currentSpeed) + ",";
    json += "\"trim\":" + String(motors.motorTrim) + ",";
    json += "\"watchdog\":" + String(watchdog.isTimedOut() ? "true" : "false") + ",";
    json += "\"uptime\":" + String(millis() / 1000);
    json += "}";
    httpServer.send(200, "application/json", json);
}

void setup() {
    Serial.begin(115200);
    delay(300);

    Serial.println("\n\n================================================");
    Serial.println("  AUTONOMOUS AI CAR - ESP8266 FIRMWARE v2.1     ");
    Serial.println("  DUAL MODE: MANUAL (ARES PRO) + AUTO (AI)      ");
    Serial.println("================================================");

    // Initialize Motor Pins & Safe Default State
    motors.init();
    Serial.println("[HARDWARE] TB6612FNG Driver initialized (Standby HIGH, 1kHz PWM)");

#if USE_STATION_MODE
    Serial.print("[WIFI] Connecting to Phone Hotspot: ");
    Serial.println(STA_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(STA_SSID, STA_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 25) {
        delay(400);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[WIFI] Connected! Assigned IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("\n[WIFI] Failed to connect! Falling back to SoftAP Mode.");
        WiFi.mode(WIFI_AP);
        WiFi.softAP(AP_SSID, AP_PASSWORD);
        Serial.println("[WIFI] SoftAP Online: " + String(AP_SSID) + " (IP: " + WiFi.softAPIP().toString() + ")");
    }
#else
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASSWORD);
    Serial.println("[WIFI] SoftAP Online: " + String(AP_SSID));
    Serial.println("[WIFI] Access Point IP: " + WiFi.softAPIP().toString());
#endif

    // Start UDP Server on Port 8888
    udpServer.begin();

    // Start HTTP Diagnostic Server on Port 80
    httpServer.on("/ping", HTTP_GET, handleHttpPing);
    httpServer.on("/status", HTTP_GET, handleHttpStatus);
    httpServer.begin();
    Serial.println("[HTTP] Diagnostic server active on port 80");

    watchdog.feed();
    Serial.println("[SYSTEM] Ready for Dual-Mode (Manual DRIVE + Auto Action) Commands.");
}

void loop() {
    // 1. Process High-Speed UDP Packets
    VehicleCommand cmd;
    if (udpServer.parsePacket(cmd)) {
        watchdog.feed();

        if (cmd.isDirectDrive) {
            // Manual Mode: Differential steering from Cosmic Byte Ares Pro
            motors.driveDirect(cmd.leftPwm, cmd.rightPwm);
        } else {
            // Autonomous Mode: AI Traffic Sign Decisions
            motors.setTrim(cmd.trim);

            if (cmd.action == "FORWARD") {
                motors.forward(cmd.speed);
            } else if (cmd.action == "BACKWARD") {
                motors.backward(cmd.speed);
            } else if (cmd.action == "LEFT") {
                motors.turnLeft(cmd.speed);
            } else if (cmd.action == "RIGHT") {
                motors.turnRight(cmd.speed);
            } else if (cmd.action == "STOP") {
                motors.stop();
            } else if (cmd.action == "HEARTBEAT") {
                // Heartbeat only feeds watchdog without altering state
            }
        }
    }

    // 2. Handle HTTP Diagnostic Requests
    httpServer.handleClient();

    // 3. Check Safety Watchdog
    watchdog.check(motors);
}
