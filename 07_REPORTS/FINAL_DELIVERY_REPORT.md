# Final Engineering Delivery & Handover Report

**Project Title:** AI-Based Autonomous Car Using Real-Time Traffic Sign Detection  
**Engineering Discipline:** Senior Embedded Systems + AI/ML + Android + Robotics  
**Version:** 2.0.0 (Production Release)  
**Date:** November 2026  

---

## 1. What Was Implemented

1. **Native Android Vision Application (`03_ANDROID_APP/`):**
   - Engineered in Kotlin with Android Studio, CameraX, and TensorFlow Lite.
   - On-device real-time YOLOv8 neural network inference (no cloud or internet required).
   - High-tech custom HUD overlay (`OverlayView`) rendering bounding boxes, confidence badges, corner brackets, and telemetry gauges.
   - Non-blocking coroutine-based UDP client communicating with ESP8266 on Port 8888.
   - Emergency STOP button and manual keyboard/UI override.

2. **Modular Decision Engine (`DecisionEngine.kt`):**
   - 6-stage verification pipeline: Confidence Filter $\rightarrow$ Geometric Aspect Ratio Filter $\rightarrow$ Temporal Consecutive-Frame Debounce $\rightarrow$ Proximity Zone Distance Estimator $\rightarrow$ Maneuver Lock $\rightarrow$ Cooldown Prevention.
   - Regulates speed: Cruise (PWM 700), Deceleration approach (PWM 480–520), Turning maneuver (PWM 760), and Regulatory Stop Hold (3.0 seconds).

3. **Production ESP8266 Firmware (`04_ESP8266_FIRMWARE/`):**
   - Modular PlatformIO structure + 1-click standalone Arduino IDE sketch (`esp8266_firmware.ino`).
   - Hardware boot-strap pin safety verified (GPIO 15, GPIO 0, GPIO 2 isolated).
   - Low-latency UDP datagram receiver on Port 8888 with automatic sequence and timestamp validation.
   - 1.0-second hardware fail-safe watchdog timer.
   - Dynamic wireless motor balance trim ($\pm 100$) to compensate for TT motor mechanical variance.

4. **Machine Learning Toolchain (`02_AI_MODEL/`):**
   - Training pipeline (`train.py`), test-split benchmark evaluator (`evaluate.py`), multi-format exporter (`export_model.py` for ONNX/TFLite/NCNN), and latency benchmarking suite (`benchmark.py`).
   - Validated ONNX format (input `[1, 3, 640, 640]`, output `[1, 10, 8400]`).

5. **Python Development & Diagnostic Suite (`05_PYTHON_TOOLS/`):**
   - Dataset validation tool (`validate_dataset.py`), model architecture comparison matrix (`compare_models.py`), wireless UDP/HTTP latency testing tool (`test_communication.py`), camera stream diagnostic tool (`test_camera.py`), and desktop HUD simulator (`pc_telemetry_hud.py`).

6. **Comprehensive 22-Part Markdown Documentation (`01_DOCUMENTATION/`):**
   - Complete guides numbered sequentially from `01_START_HERE.md` to `22_FINAL_CHECKLIST.md`.

---

## 2. What Was Retained & What Was Removed

### Retained:
- **`dataset/`**: The complete 6,000-image dataset (4200 train / 1200 val / 600 test) with annotations in YOLO format.
- **`models/best.pt`**: Reorganized to `02_AI_MODEL/weights/best_yolov8s.pt` (11.14M params, 99.5% mAP@50).
- **`models/best_yolov8n_backup.pt`**: Reorganized to `02_AI_MODEL/weights/best_yolov8n.pt` (3.13M params, 99.5% mAP@50).
- **`Autonomous-Car.zip`**: Preserved untouched as raw immutable archive backup.

### Archived & Removed:
- **`detect.py`**: Archived to `_backup/detect.py`. Removed from production because it hardcoded obsolete training paths, ran with an insecure 0.10 confidence threshold, and had no vehicle actuation logic.
- **Redundant Intermediate Checkpoints**: Filtered out via `.gitignore` to prevent repository bloat.

---

## 3. Selected AI Model & Engineering Justification

**Selected Primary Mobile Model:** **YOLOv8 Nano (`yolov8n`)**
- **Parameters:** 3.13 Million (vs 11.14M for Small)
- **Model Size:** 6.2 MB (vs 22.5MB for Small)
- **Inference Latency on Phone:** ~22 ms (~45 FPS) on mobile CPU/GPU
- **Computational Cost:** 8.6 GFLOPs (vs 28.5 GFLOPs for Small)
- **Empirical Accuracy:**
  - Test Precision: **100.00%**
  - Test Recall: **100.00%**
  - Test mAP@50: **99.50%**
  - Test mAP@50-95: **97.25%**
- **Justification:** Achieves identical 99.50% mAP@50 on all 6 traffic sign classes while consuming 3.3x less energy and half the memory of YOLOv8s.

---

## 4. Hardware Configuration

| Component | Verified Specification | Connection / Power Source |
| :--- | :--- | :--- |
| **Microcontroller** | NodeMCU ESP8266 (ESP-12E) | Powered via VIN at **5.1V DC** from Buck Converter. |
| **Motor Driver** | TB6612FNG Dual MOSFET H-Bridge | Logic VCC at 5.1V; Motor VM directly from 7.4V battery. |
| **Drive Motors** | 2x TT DC Gear Motors (1:48) | Connected to AO1/AO2 (Left) and BO1/BO2 (Right). |
| **Power Supply** | 2S 18650 Li-ion Battery Pack | 7.4V Nominal (8.4V Peak) protected by 3A fast fuse. |
| **Buck Converter** | LM2596 / Mini360 Switching Regulator | Steps 7.4V battery rail down to **5.10V – 5.20V DC**. |
| **Decoupling** | 220µF–470µF 16V Electrolytic Capacitor | Solder directly across TB6612FNG `VM` and `GND`. |
| **Ground Reference**| **Single Common Ground Bus** | Connects Battery (-), Buck GND, NodeMCU GND, TB6612 GND. |
| **Smartphone** | Android Redmi Series | Mounted on front chassis with 10°–15° upward tilt. |

---

## 5. Software Configuration

- **Android App:** Kotlin, Min SDK 24, Target SDK 34, CameraX, TensorFlow Lite 2.14.0, Coroutines.
- **ESP8266 Firmware:** Arduino C++, ESP8266 Core 3.1.2+, 80/160 MHz CPU, 115200 baud Serial, UDP 8888.
- **Python Toolchain:** Python 3.10–3.14, PyTorch 2.14.1, Ultralytics 8.4+, OpenCV 4.13+, ONNX 1.23+.

---

## 6. Installation Sequence

1. **Hardware:** Follow [`01_DOCUMENTATION/04_COMPLETE_WIRING_GUIDE.md`](01_DOCUMENTATION/04_COMPLETE_WIRING_GUIDE.md). Set buck converter to 5.1V with multimeter before inserting NodeMCU.
2. **Firmware:** Open [`04_ESP8266_FIRMWARE/esp8266_firmware.ino`](04_ESP8266_FIRMWARE/esp8266_firmware.ino) in Arduino IDE and flash NodeMCU at 115200 baud.
3. **Android App:** Open [`03_ANDROID_APP`](03_ANDROID_APP) in Android Studio, connect phone with USB debugging enabled, and tap **Run 'app'**.
4. **Networking:** On phone, connect to Wi-Fi SSID `AutonomousCar_AP` (Password: `12345678`).

---

## 7. Test Results Matrix

All 15 required verification stages are documented in [`TEST_RESULTS.md`](TEST_RESULTS.md).
- Automated ML unit tests: **PASSED** ([`test_model_inference.py`](06_TESTING/model_tests/test_model_inference.py) detected sample stop sign with 95.24% confidence).
- Automated decision logic tests: **PASSED** ([`test_decision_engine.py`](06_TESTING/integration_tests/test_decision_engine.py) verified debounce, stop priority, and state transitions).
- Automated UDP protocol tests: **PASSED** ([`test_udp_mock.py`](06_TESTING/communication_tests/test_udp_mock.py) verified packet parsing).

---

## 8. Known Limitations & User Residual Verification

1. **Open-Loop Steering Limits:** Without wheel encoders, turn angles and straight-line tracking rely on calibrated timing ($T_{\text{turn}} = 0.85\text{s}$) and motor trim. A calibration procedure is documented in [`01_DOCUMENTATION/18_MOTOR_CALIBRATION.md`](01_DOCUMENTATION/18_MOTOR_CALIBRATION.md).
2. **Lighting Sensitivity:** In extreme low-light conditions, mobile camera shutter speed drops, causing motion blur. Maintain adequate track illumination.
3. **Sign Visual Domain:** The signs must match the blue circular/octagonal icons present in the training dataset.

---

## 9. Launch Command Quick Reference

```powershell
# 1. Run Pre-Flight Automated Unit Tests:
python "06_TESTING/model_tests/test_model_inference.py"
python "06_TESTING/integration_tests/test_decision_engine.py"
python "06_TESTING/communication_tests/test_udp_mock.py"

# 2. Validate Dataset:
python "05_PYTHON_TOOLS/scripts/validate_dataset.py" --data-dir dataset

# 3. Test Wireless ESP8266 Link (from PC):
python "05_PYTHON_TOOLS/scripts/test_communication.py" --esp-ip 192.168.4.1

# 4. Optional: Launch Master Desktop Cockpit HUD (PC Simulation):
python "05_PYTHON_TOOLS/scripts/pc_telemetry_hud.py" --stream-url "http://192.168.4.2:4747/video" --esp-ip "192.168.4.1" --conf 0.65
```
