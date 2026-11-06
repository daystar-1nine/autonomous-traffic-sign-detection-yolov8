# 10 - ESP8266 Dual-Mode Firmware Architecture & Pinout Verification

---

## 1. Purpose
This document details the firmware architecture, boot-strap pin safety constraints, and dual-protocol command execution implemented on the **NodeMCU ESP8266 ESP-12E** microcontroller.

---

## 2. Hardware Pinout Verification
The NodeMCU pin configuration preserves boot-strapping integrity:
- **GPIO 15 (D8):** Must be LOW at boot. Connected to TB6612 `STBY` (pulled LOW internally until firmware elevates HIGH).
- **GPIO 0 (D3):** Must be HIGH at boot. Connected to `AIN2` (CMOS high impedance).
- **GPIO 2 (D4):** Must be HIGH at boot. Connected to onboard Blue Status LED.

### Pinout Table:
| NodeMCU ESP8266 Pin | TB6612FNG Pin | Purpose | Direction |
| :--- | :--- | :--- | :--- |
| **D1 (GPIO 5)** | **PWMA** | Motor A (Left) PWM Speed | Output (PWM 1kHz) |
| **D2 (GPIO 4)** | **AIN1** | Motor A (Left) Direction 1 | Output |
| **D3 (GPIO 0)** | **AIN2** | Motor A (Left) Direction 2 | Output |
| **D5 (GPIO 14)** | **BIN1** | Motor B (Right) Direction 1 | Output |
| **D6 (GPIO 12)** | **BIN2** | Motor B (Right) Direction 2 | Output |
| **D7 (GPIO 13)** | **PWMB** | Motor B (Right) PWM Speed | Output (PWM 1kHz) |
| **D8 (GPIO 15)** | **STBY** | TB6612 Driver Standby Enable | Output (Active HIGH) |
| **D4 (GPIO 2)** | **LED** | Telemetry Status LED | Output (Active LOW) |

---

## 3. Dual-Protocol Parser Implementation
The firmware seamlessly parses two packet families on UDP Port 8888:

1. **Direct Differential Drive Packet (Manual Ares Pro Mode):**
   ```text
   CMD:DRIVE:<LEFT_PWM>:<RIGHT_PWM>:<SEQ>
   Example: CMD:DRIVE:750:750:1042
   ```
   - Automatically executes `motors.driveDirect(leftPwm, rightPwm)`.
   - Feeds communication watchdog.
   - Echoes `ACK:DRIVE:<SEQ>:<RSSI>`.

2. **Autonomous Action Packet (Autonomous AI Vision Mode):**
   ```text
   CMD:<ACTION>:<SPEED>:<TRIM>:<SEQ>
   Example: CMD:FORWARD:700:0:1043
   ```
   - Executes `FORWARD`, `BACKWARD`, `LEFT`, `RIGHT`, `STOP`.
   - Feeds communication watchdog.
   - Echoes `ACK:<ACTION>:<SEQ>:<RSSI>`.

---

## 4. Flashing Instructions
1. Open `04_ESP8266_FIRMWARE/esp8266_firmware.ino` in Arduino IDE.
2. Select Board: **NodeMCU 1.0 (ESP-12E Module)**.
3. Upload speed: **115200**.
4. Click **Upload**.

---

## 5. Verification Checklist
- [ ] NodeMCU boots into SoftAP without hanging.
- [ ] Serial monitor displays `[UDP] Listening on Port 8888`.
- [ ] TB6612 Standby elevates HIGH after boot.
