# 13 - NodeMCU ESP8266 Firmware Flashing Guide

This document covers compiling and uploading the production embedded firmware to the **NodeMCU ESP8266 (ESP-12E)** board using the Arduino IDE.

---

## 🛠️ Step 1: Open Firmware in Arduino IDE

1. Connect the NodeMCU to your computer using a Micro-USB data cable (ensure the cable supports data, not charging only).
2. Launch **Arduino IDE**.
3. Open the single-file firmware:
   ```text
   S:\Kaushalya 2.0\R with CV\04_ESP8266_FIRMWARE\esp8266_firmware.ino
   ```

---

## ⚙️ Step 2: Configure Arduino IDE Settings

Under the **Tools** menu, select the following exact board settings:

| Setting | Value |
| :--- | :--- |
| **Board** | **NodeMCU 1.0 (ESP-12E Module)** |
| **Upload Speed** | **921600** (or 115200 if upload fails) |
| **CPU Frequency** | **80 MHz** (or 160 MHz for maximum UDP packet rate) |
| **Flash Size** | **4MB (FS:2MB OTA:~1019KB)** |
| **Port** | Select the active COM port (e.g. `COM3`, `COM4`, `COM5`) |

> [!TIP]
> **COM Port Driver:** If no COM port appears, your computer is missing the USB-to-UART bridge driver. NodeMCU boards use either the **CH340G** or **CP2102** chip. Download and install the driver:
> - [CH340 Windows Driver](http://www.wch-ic.com/downloads/CH341SER_EXE.html)
> - [CP210x Windows Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

---

## 🚀 Step 3: Compile & Upload Firmware

1. Click the **Upload** arrow button in the Arduino IDE toolbar (or press `Ctrl + U`).
2. Watch the bottom output console. You will see:
   ```text
   Archiving built core (caching) in ...
   Writing at 0x00000000... (10 %)
   Writing at 0x00010000... (30 %)
   Writing at 0x00020000... (60 %)
   Writing at 0x00040000... (100 %)
   Leaving...
   Hard resetting via RTS pin...
   ```
3. Upload complete!

---

## 🔍 Step 4: Verify via Serial Monitor

1. Open **Tools → Serial Monitor** in Arduino IDE.
2. In the bottom-right corner of the Serial Monitor, set the baud rate to **115200 baud**.
3. Press the physical **RST** button on the NodeMCU.
4. You should see the startup banner:
   ```text
   ================================================
     AI AUTONOMOUS CAR: ESP8266 FIRMWARE v2.0      
   ================================================
   [HARDWARE] TB6612FNG Driver initialized (Standby HIGH, 1kHz PWM)
   [WIFI] Access Point Started: AutonomousCar_AP
   [WIFI] Car IP Address: 192.168.4.1
   [UDP] Listening on Port 8888
   ```

---

👉 **Next Step:** Proceed to [`14_WIFI_SETUP.md`](14_WIFI_SETUP.md) to pair the phone and vehicle.
