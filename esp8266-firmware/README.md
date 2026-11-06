# ESP8266 NodeMCU Firmware (v2.0)

This directory contains the production embedded firmware for the **NodeMCU ESP8266 (ESP-12E)** controlling two TT DC gear motors via a **TB6612FNG** dual motor driver.

---

## 📁 Directory Structure
```text
04_ESP8266_FIRMWARE/
├── include/
│   ├── pin_config.h       # Pinout definitions & boot-strap pin verification
│   ├── motor_driver.h     # TB6612FNG driver with soft PWM acceleration
│   ├── udp_protocol.h     # Sub-3ms UDP receiver with ACK & sequence validation
│   └── watchdog.h         # 1.0s fail-safe hardware watchdog timer
├── src/
│   └── main.cpp           # Modular PlatformIO main loop
├── esp8266_firmware.ino   # Standalone Arduino IDE sketch for 1-click flashing
├── platformio.ini         # PlatformIO project configuration
└── README.md              # Documentation (this file)
```

---

## ⚡ Flashing Instructions

### Option A: Using Arduino IDE (Recommended for Beginners)
1. Install [Arduino IDE](https://www.arduino.cc/en/software).
2. Add ESP8266 Board Manager URL in **File → Preferences**:
   ```text
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
3. Install **esp8266 by ESP8266 Community** via **Tools → Board → Boards Manager**.
4. Open [`esp8266_firmware.ino`](esp8266_firmware.ino).
5. Select Board: **NodeMCU 1.0 (ESP-12E Module)** and choose your COM port.
6. Click **Upload**.
7. Open Serial Monitor at **115200 baud** to see the Access Point status and IP address (`192.168.4.1`).

### Option B: Using PlatformIO (VS Code)
1. Open this folder in VS Code with PlatformIO extension installed.
2. Run build: `pio run`
3. Upload to board: `pio run --target upload`
4. Monitor serial: `pio device monitor`

---

## 🔌 Pin Connections (NodeMCU ↔ TB6612FNG)

| NodeMCU Pin | GPIO | TB6612 Pin | Function |
| :---: | :---: | :---: | :--- |
| **D1** | GPIO 5 | **PWMA** | Left Motor Speed PWM (0-1023) |
| **D2** | GPIO 4 | **AIN1** | Left Motor Direction 1 |
| **D3** | GPIO 0 | **AIN2** | Left Motor Direction 2 |
| **D5** | GPIO 14 | **BIN1** | Right Motor Direction 1 |
| **D6** | GPIO 12 | **BIN2** | Right Motor Direction 2 |
| **D7** | GPIO 13 | **PWMB** | Right Motor Speed PWM (0-1023) |
| **D8** | GPIO 15 | **STBY** | Driver Standby Enable (Active HIGH) |
| **VIN** | 5V | **VCC** | Driver Logic Power (+5.0V from Buck Converter) |
| **GND** | GND | **GND** | Common Ground Bus |
| **Battery (+)** | 7.4V | **VM** | Direct Motor Power |
