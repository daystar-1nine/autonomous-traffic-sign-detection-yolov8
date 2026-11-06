# 20. TROUBLESHOOTING & FAULT DIAGNOSTICS MATRIX
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Quick Triage Diagnostic Table

| Symptom / Fault | Root Cause | Engineering Solution |
| :--- | :--- | :--- |
| **NodeMCU will not boot (LED flashes and halts)** | GPIO 15 (D8) pulled HIGH or GPIO 0 (D3) pulled LOW during power-up | Verify wiring: TB6612 `STBY` must be on D8 (pulldown). Ensure no external sensors pull D8 HIGH at startup. |
| **ESP8266 reboots randomly when motors start** | Severe voltage drop (brownout) on the 5V rail caused by motor inrush current | Calibrate LM2596 buck converter to 5.15V. Ensure battery is charged $\ge 7.4\text{V}$. Add a $470\mu\text{F}$ capacitor across LM2596 OUT. |
| **Motors do not rotate, but serial monitor shows commands** | TB6612 `STBY` pin is LOW, or motor supply `VM` is disconnected | Verify TB6612 `STBY` is receiving 3.3V logic HIGH. Verify battery (+) is connected to `VM` pin. Check ground connection. |
| **Car turns in opposite direction of joystick command** | Motor terminal wiring polarity reversed | Swap the two wires connected to TT motor terminals `AO1/AO2` or `BO1/BO2`, or invert steering axis in `DifferentialDriveController.kt`. |
| **Car veers off course when driving straight** | Mechanical friction discrepancy between the two TT gearboxes | Adjust `leftTrimFactor` and `rightTrimFactor` in `DifferentialDriveController.kt` until vehicle tracks straight. |
| **Android App shows Camera preview, but 0 FPS / No Detections** | Model file missing in assets, or CameraX analyzer throwing unhandled exception | Verify `yolov8n.onnx` or `yolov8n.tflite` is present in `android-app/app/src/main/assets/`. Check `adb logcat -s YoloDetector`. |
| **Cosmic Byte Ares Pro connects via Bluetooth, but app does not react** | Gamepad is in X-Input or D-Input PC mode instead of Android HID mode | Power down controller. Reconnect by pressing **[HOME] + [A]** for 3 seconds to enter Android standard HID gamepad mode. |
| **Watchdog triggers constantly (`[WATCHDOG] Communication timeout`)** | Wi-Fi UDP packet loss due to RF interference or sleep policy | On Samsung A36 5G, go to Wi-Fi settings for `AutonomousCar_AP`, set **MAC Type** to `Phone MAC` and disable battery optimization for the app. |

---

## 2. Interactive Diagnostic Serial Monitor

Connect the NodeMCU to your workstation via Micro-USB and open the Serial Monitor at **115200 baud**. The firmware outputs real-time diagnostic telemetry:

```
================================================
  AUTONOMOUS AI CAR - ESP8266 FIRMWARE v2.1     
  DUAL MODE: MANUAL (ARES PRO) + AUTO (AI)      
================================================
[TB6612] Motor driver initialized. STBY = HIGH.
[WIFI] SoftAP Access Point Started: AutonomousCar_AP
[WIFI] Car IP Address: 192.168.4.1
[UDP] Listening on Port 8888 (Direct DRIVE + Action Commands)
[HTTP] Diagnostic Web Server running on Port 80.
[HEARTBEAT] Ready for connection...
```

When commands arrive, the console echoes:
```
[UDP RECV] CMD:DRIVE:750:750:1 -> L:750, R:750
[UDP RECV] CMD:STOP:0:0:2 -> Vehicle Halting
```
If packet loss exceeds 1.0 second:
```
[WATCHDOG] Communication timeout! Emergency auto-stop engaged.
```

---

## 3. Web Diagnostic Server Verification

While connected to `AutonomousCar_AP`, open a browser on the smartphone and navigate to:
- `http://192.168.4.1/ping` -> Returns live server uptime and signal strength:
  `PONG | Mode: AP | IP: 192.168.4.1 | Uptime: 45s`
- `http://192.168.4.1/status` -> Returns JSON telemetry:
  `{"action":"STOP","speed":0,"trim":0,"watchdog":false,"uptime":45}`
