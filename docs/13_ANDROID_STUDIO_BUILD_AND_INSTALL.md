# 13. ANDROID STUDIO BUILD & INSTALLATION GUIDE
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Prerequisites Checklist

Before building the APK, verify:
- [x] Android Studio Hedgehog / Iguana / Jellyfish installed.
- [x] Android SDK Platform 34 and Build-Tools 34.0.0 installed.
- [x] Samsung Galaxy A36 5G connected via USB with **USB Debugging** enabled.
- [x] Model assets present in `android-app/app/src/main/assets/`:
  - `yolov8n.onnx` (or `yolov8n.tflite`)
  - `labels.txt`

---

## 2. Building & Installing from Android Studio

1. **Open Project:** Launch Android Studio, select **Open**, and navigate to the `android-app/` directory.
2. **Sync Gradle:** Click **Sync Project with Gradle Files**. Wait for Gradle dependencies to resolve.
3. **Select Build Variant:** Open the **Build Variants** tab on the left margin. Ensure `debug` (or `release`) is selected for the `app` module.
4. **Target Device Selection:** In the top toolbar device selector, choose **Samsung SM-A366B** (Galaxy A36 5G).
5. **Run Application:** Press the green **Run (Shift+F10)** button. Android Studio will compile, link, package, and deploy the APK directly to your smartphone.

---

## 3. Building via Command Line (Gradle Wrapper)

To build a standalone APK without launching the full IDE:

```bash
cd android-app

# Windows PowerShell:
.\gradlew assembleDebug

# Linux / macOS:
./gradlew assembleDebug
```

The compiled APK will be located at:
`android-app/app/build/outputs/apk/debug/app-debug.apk`

### Installing via ADB:
```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## 4. Required Runtime Permissions

When launched for the first time, the application requests the following Android runtime permissions:
1. **`android.permission.CAMERA`:** Required for CameraX to access the rear camera sensor.
2. **`android.permission.BLUETOOTH_CONNECT` & `BLUETOOTH_SCAN`:** Required on Android 12+ (API 31+) to discover and communicate with the Cosmic Byte Ares Pro gamepad.
3. **`android.permission.INTERNET` & `ACCESS_WIFI_STATE`:** Required to transmit low-latency UDP packets to the ESP8266 Access Point (`192.168.4.1:8888`).

Grant all permissions when prompted.
