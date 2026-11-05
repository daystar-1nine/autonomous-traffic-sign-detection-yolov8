# 12 - Android Application Build & Installation Guide

This document covers compiling, testing, and installing the **Autonomous AI Car** Android APK on your smartphone.

---

## 🚀 Building & Running from Android Studio

1. In Android Studio, ensure `03_ANDROID_APP` is open and Gradle sync has finished.
2. Select your connected Redmi phone from the target device selector in the main toolbar.
3. Click the green **Run 'app'** button (or press `Shift + F10`).
4. Android Studio will execute:
   - Kotlin compilation (`kapt` / `compileDebugKotlin`)
   - Asset bundling (`yolov8n.tflite` packaged into APK)
   - APK installation via `adb install`
   - Activity launch: `com.autonomous.aicontrol.MainActivity`
5. On the phone screen, grant **Camera** and **Location/Wi-Fi** runtime permissions.

---

## 📦 Building a Standalone Release APK

To create an independent `.apk` file that you can transfer and install on any Android phone without a computer:

### Via Android Studio Terminal:
```bash
# In 03_ANDROID_APP root directory:
./gradlew assembleDebug
```

The compiled APK will be generated at:
```text
03_ANDROID_APP/app/build/outputs/apk/debug/app-debug.apk
```

You can copy `app-debug.apk` directly to your phone's *Downloads* folder via USB and tap to install!

---

## 🔍 Pre-Flight App Checks
Once installed, open the app:
1. Verify live camera feed renders smoothly at **30+ FPS**.
2. Verify top bar shows:
   - `FPS: ~30.0`
   - `AI: ~20-35ms` (On-device neural inference time)
   - `CAR UDP: DISCONNECTED` (Will change to latency in ms once connected to car Wi-Fi).
3. Tap **EMERGENCY STOP** to verify the red safety lock engages.

---

👉 **Next Step:** Proceed to [`13_ESP8266_SETUP.md`](13_ESP8266_SETUP.md) to set up and flash the car's microcontroller.
