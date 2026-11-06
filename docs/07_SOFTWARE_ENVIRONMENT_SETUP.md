# 07. SOFTWARE ENVIRONMENT & TOOLCHAIN SETUP
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Overview of Developer Toolchain

Developing and maintaining the complete autonomous vehicle software stack requires four core developer environments:
1. **Python 3.10+ Machine Learning Environment:** Model training, evaluation, export, dataset conversion, simulation.
2. **Android Studio Hedgehog / Iguana / Jellyfish (API 34+):** Native Kotlin application development, CameraX, LiteRT/TFLite runtime, UI/HUD.
3. **VS Code + PlatformIO or Arduino IDE 2.x:** ESP8266 embedded firmware compilation, flashing, serial monitor telemetry.
4. **Android Debug Bridge (ADB):** USB and Wireless ADB debugging and APK deployment.

---

## 2. Android Studio & SDK Configuration

1. **Install Android Studio:**
   - Download Android Studio (latest stable release) with Android SDK Platform 34 (Android 14) and Android SDK Build-Tools 34.0.0.
   - Install Android NDK (v25+) and CMake (v3.22+) if compiling native C++ extensions.
2. **Enable Developer Options on Samsung Galaxy A36 5G:**
   - Open **Settings** -> **About Phone** -> **Software Information**.
   - Tap **Build Number** 7 times rapidly until "Developer mode has been turned on" appears.
   - Return to **Settings** -> **Developer Options**.
   - Toggle **USB Debugging** to ON.
   - Toggle **Wireless Debugging** to ON (optional for tetherless in-car debugging).
3. **Import Project:**
   - Open Android Studio -> Select **Open an Existing Project** -> Navigate to `android-app/`.
   - Allow Gradle to sync dependencies automatically.

---

## 3. Microcontroller Firmware Toolchain (PlatformIO / Arduino IDE)

### Option A: VS Code + PlatformIO (Recommended for Production)
1. Install VS Code and the official **PlatformIO IDE** extension.
2. Open the `esp8266-firmware/` directory. PlatformIO will automatically parse `platformio.ini` and download the `espressif8266` toolchain and libraries.
3. Connect NodeMCU ESP8266 via Micro-USB cable to your workstation.
4. Click the PlatformIO **Upload** checkmark in the bottom status bar.

### Option B: Arduino IDE 2.x (Quick 1-Click Flashing)
1. Install Arduino IDE 2.3+.
2. Open **File** -> **Preferences**. Add this URL to **Additional Boards Manager URLs**:
   `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
3. Open **Tools** -> **Board** -> **Boards Manager**. Search for `esp8266` and install version `3.1.2`.
4. Select **Tools** -> **Board** -> **ESP8266 Boards** -> **NodeMCU 1.0 (ESP-12E Module)**.
5. Set:
   - CPU Frequency: `80 MHz` (or `160 MHz` for maximum packet processing throughput)
   - Flash Size: `4MB (FS:2MB OTA:~1019KB)`
   - Upload Speed: `115200` or `921600`
6. Open `esp8266-firmware/esp8266_firmware.ino` and click **Upload**.
