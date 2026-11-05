# Android AI Vision Brain Application

This directory contains the complete **native Android application** engineered in **Kotlin** with **CameraX** and **TensorFlow Lite (TFLite)** to turn a smartphone into the primary on-device artificial intelligence vision system for the autonomous car.

---

## 📱 Features

1. **CameraX Engine**: Native zero-lag camera frame streaming with backpressure strategy set to `KEEP_ONLY_LATEST`.
2. **On-Device YOLOv8n Inference**: Runs neural network detection locally on mobile CPU/GPU without cloud or internet.
3. **Modular Decision Engine**:
   - Temporal debounce filter (requires 2 consecutive frame matches to prevent false flickers).
   - Spatial proximity zone estimator (determines when sign is far vs when vehicle reaches the turn/stop line).
   - Maneuver-locking turning controller (executes full calibrated 90° arc).
   - Regulatory stop holding timer (holds at stop line for 3 seconds).
4. **Low-Latency UDP Communication**: Sends direct datagram commands to the ESP8266 Access Point (`192.168.4.1:8888`) with $<3$ms wireless latency.
5. **Futuristic Cockpit HUD**: Custom `OverlayView` drawing bounding boxes, confidence badges, corner brackets, and telemetry gauges.
6. **Fail-Safe Emergency Controls**: Instant red Emergency Brake button and Auto/Manual toggle.

---

## 🛠️ Build & Installation Guide (Android Studio)

1. Open **Android Studio** (Hedgehog, Iguana, or Koala).
2. Select **File → Open** and choose the `03_ANDROID_APP/` folder.
3. Wait for Gradle to finish syncing project dependencies.
4. Copy the exported model `02_AI_MODEL/exports/yolov8n.tflite` into:
   ```text
   03_ANDROID_APP/app/src/main/assets/yolov8n.tflite
   ```
5. Connect your **Redmi Android Smartphone** via USB cable:
   - Enable **Developer Options** (Tap *MIUI/OS Version* 7 times in *About Phone*).
   - Enable **USB Debugging** and **Install via USB**.
6. Select your Redmi device from the device dropdown in Android Studio.
7. Click **Run 'app'** (`Shift + F10`).
8. Grant Camera and Location permissions when prompted.
9. Connect your phone's Wi-Fi to the car's Access Point:
   - SSID: `AutonomousCar_AP`
   - Password: `12345678`
10. The app will immediately start real-time vision detection and autonomous vehicle control!
