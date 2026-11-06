# 🚗 Autonomous AI Traffic Sign Detection & Dual-Mode Robotic Car

[![Platform](https://img.shields.io/badge/Platform-Samsung%20Galaxy%20A36%205G-blue?logo=samsung)](docs/02_HARDWARE_SPECIFICATIONS.md)
[![SoC](https://img.shields.io/badge/SoC-Snapdragon%206%20Gen%203-red?logo=qualcomm)](docs/02_HARDWARE_SPECIFICATIONS.md)
[![Android](https://img.shields.io/badge/Android-Kotlin%20%7C%20CameraX%20%7C%20LiteRT-3DDC84?logo=android)](android-app/)
[![Model](https://img.shields.io/badge/Model-YOLOv8n%20(3.13M)%20%7C%2099.5%25%20mAP50-00FFFF?logo=yolo)](models/)
[![Microcontroller](https://img.shields.io/badge/MCU-NodeMCU%20ESP8266%20v2.1-red?logo=espressif)](esp8266-firmware/)
[![Controller](https://img.shields.io/badge/Gamepad-Cosmic%20Byte%20Ares%20Pro-purple?logo=bluetooth)](docs/14_COSMIC_BYTE_ARES_PRO_SETUP.md)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing%20(6%2F6)-brightgreen)](tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade, complete dual-mode robotic vehicle system combining cutting-edge edge computer vision with real-time embedded motor control. The vehicle uses a **Samsung Galaxy A36 5G (Qualcomm Snapdragon 6 Gen 3)** smartphone mounted to its chassis as the primary vision and AI processing brain, communicating with a **NodeMCU ESP8266** microcontroller and **TB6612FNG** dual motor driver over a low-latency 2.4 GHz Wi-Fi UDP link.

---

## 🎮 Dual-Mode Driving Capabilities

1. **Manual Gamepad Mode (Cosmic Byte Ares Pro):**
   - Direct Bluetooth 5.3 HID connection with sub-8ms latency.
   - Proportional differential steering with configurable center deadband ($0.10$).
   - S-curve acceleration slew rate limiting (85 PWM/tick) to eliminate wheel slippage and motor inrush current spikes.
   - 3 switchable speed profiles on the fly: **`ECO` (50% PWM)**, **`NORMAL` (75% PWM)**, and **`SPORT` (100% PWM)**.
   - Skid-steer differential in-place 360° pivot turning.
2. **Autonomous Vision Mode:**
   - Real-time road perception via CameraX at 30+ FPS.
   - On-device edge neural detection using **YOLOv8n** (3.13M parameters, 13.8 ms on Adreno 710 GPU delegate, 99.5% mAP50).
   - 6-Class traffic sign recognition: `left_turn`, `straight_ahead`, `right_turn`, `dead_end`, `no_entry`, `stop`.
   - Multi-frame temporal persistence debounce filter ($300\text{ ms}$ window) and geometric bounding box verification.
3. **Emergency Stop (Hardware Preemption):**
   - Unconditionally overrides both Manual and Autonomous modes.
   - Immediate high-side active braking halting the car in $<150\text{ ms}$.
   - Automatic triggers on controller disconnection or 1,000 ms Wi-Fi packet loss watchdog.

---

## 📌 Master System Architecture

```text
 ┌────────────────────────────────────────────────────────┐
 │            COSMIC BYTE ARES PRO GAMEPAD                │
 │   • Bluetooth 5.3 Native Input (Sub-8ms HID Latency)   │
 │   • Left Stick: Throttle & Differential Steering       │
 │   • Button A: Manual | Button B: Auto | Button X: STOP │
 └───────────────────────────┬────────────────────────────┘
                             │ Bluetooth HID (<8ms)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │         SAMSUNG GALAXY A36 5G (AI PROCESSING BRAIN)    │
 │   • Qualcomm Snapdragon 6 Gen 3 (Octa-core 4nm)        │
 │   • Adreno 710 GPU & Hexagon NPU Acceleration          │
 │   • AresProController & DifferentialDriveController    │
 │   • Centralized ControlModeManager (Single Owner Lock) │
 │   • CameraX 1080p @ 30 FPS Stream                      │
 │   • YOLOv8n / LiteRT / TFLite / ONNX Runtime Mobile    │
 │   • Cockpit Telemetry HUD with Live Gamepad Diagnostic │
 └───────────────────────────┬────────────────────────────┘
                             │ Low-Latency UDP Datagrams (Port 8888, <2ms)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │             EMBEDDED ACTUATION CONTROLLER              │
 │               (NodeMCU ESP8266 ESP-12E)                │
 │   • Dual-Protocol Parser (CMD:DRIVE & Action Packets)  │
 │   • Private Standalone SoftAP (AutonomousCar_AP)       │
 │   • 1,000 ms Hardware Safety Watchdog                  │
 │   • Dynamic Wireless Motor Trim & Active Motor Brake   │
 └───────────────────────────┬────────────────────────────┘
                             │ 10-Bit Hardware PWM (1 kHz)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │           TB6612FNG DUAL H-BRIDGE MOTOR DRIVER         │
 │   • VM: 7.4V-8.4V (2S Li-ion direct) | VCC: 3.3V Logic │
 │   • Continuous 1.2A / Peak 3.2A per channel            │
 └───────────────────────────┬────────────────────────────┘
                             │ High-Current Output
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │             2 × TT DC GEARED MOTORS (1:48)             │
 │   • Differential Skid-Steer Drive Wheels               │
 └────────────────────────────────────────────────────────┘
```

---

## 🏆 Model Benchmarking Beyond YOLO (Samsung A36 5G)

Six candidate architectures were systematically evaluated against our 6,000-image dataset:

| Architecture | Developer | Params | GFLOPs | Input Res | mAP@0.5 | Size (INT8) | Adreno GPU Latency | Sustained FPS | Selection Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **YOLOv8n** | Ultralytics | 3.13M | 8.7 | 640×640 | **99.5%** | 3.3 MB | **13.8 ms** | **58 FPS** | **#1 SELECTED PRODUCTION** |
| **EfficientDet-Lite0** | Google | 4.40M | 2.5 | 320×320 | **94.8%** | 4.4 MB | 15.4 ms | 52 FPS | **#2 RECOMMENDED ECO** |
| **NanoDet-Plus** | RangiLyu | 1.17M | 0.9 | 320×320 | **93.2%** | 1.3 MB | 7.8 ms | 75 FPS | **#3 ULTRA-LIGHTWEIGHT** |
| **SSD MobileNetV2** | Google | 3.50M | 1.2 | 300×300 | **88.4%** | 3.7 MB | 10.2 ms | 68 FPS | #4 LEGACY BASELINE |
| **PP-PicoDet-S** | Baidu | 0.99M | 0.73 | 320×320 | **92.5%** | 1.1 MB | 7.0 ms | 80 FPS | #5 HIGH FRICTION EXPORT |
| **RT-DETR-Tiny** | Baidu | 19.8M | 58.0 | 640×640 | **96.2%** | 21.0 MB | 85.0 ms | 11 FPS | #6 REJECTED (THERMAL LIMIT) |

*Full analysis in [`MODEL_SELECTION_REPORT.md`](MODEL_SELECTION_REPORT.md).*

---

## 📂 Project Structure

```
├── android-app/             # Complete native Android Studio project (Kotlin, CameraX, LiteRT)
│   ├── app/src/main/assets/ # Deployed models (yolov8n.onnx, labels.txt)
│   ├── app/src/main/java/   # Controllers, DecisionEngine, UdpClient, HUD UI
│   └── build.gradle         # Dependencies & SDK 34 configuration
│
├── esp8266-firmware/        # Embedded motor control firmware
│   ├── esp8266_firmware.ino # Single-file Arduino IDE firmware (1-click flash)
│   ├── src/ & include/      # Modular PlatformIO C++ firmware
│   └── platformio.ini       # PlatformIO configuration
│
├── ai-training/             # Model training & conversion pipeline
│   ├── dataset-tools/       # yolo_to_coco.py conversion script
│   ├── notebooks/           # Jupyter training notebooks
│   └── scripts/             # train.py, evaluate.py, export_model.py
│
├── models/                  # Centralized model registry
│   ├── exported/            # Production ONNX & TFLite models
│   └── weights/             # best_yolov8n.pt & best_yolov8s.pt checkpoints
│
├── dataset/                 # 6,000-image traffic sign dataset (6 classes)
│   ├── train/ & valid/ & test/
│   ├── annotations/         # Converted COCO 1.0 JSON format annotations
│   └── data.yaml            # YOLO dataset specification
│
├── tests/                   # Automated software test harness (100% passing)
│   ├── communication_tests/ # UDP packet parsing and mock socket tests
│   ├── controller_tests/    # Differential drive math & mode manager tests
│   ├── integration_tests/   # Decision engine & debouncing tests
│   ├── model_tests/         # Tensor inference tests on real images
│   └── run_all_tests.py     # Master test runner
│
├── docs/                    # 20 Comprehensive Engineering Documentation Guides
│   ├── 01_SYSTEM_ARCHITECTURE.md
│   ├── 02_HARDWARE_SPECIFICATIONS.md
│   ├── 03_COMPONENT_SELECTION_GUIDE.md
│   ├── 04_COMPLETE_WIRING_DIAGRAM.md
│   ├── 05_POWER_DISTRIBUTION_AND_BUCK_CONVERTER.md
│   ├── ... (All 20 Technical Guides)
│
├── scripts/                 # Python utilities & PC telemetry cockpit HUD
│   ├── pc_telemetry_hud.py  # Real-time desktop simulator & telemetry viewer
│   ├── predict_image.py     # Test inference on single image
│   └── webcam.py            # Real-time PC webcam detection test
│
├── requirements.txt         # Root Python dependencies
└── README.md                # Project master documentation
```

---

## ⚡ Quick Start Guide

### 1. Flash the ESP8266 Firmware
1. Open `esp8266-firmware/esp8266_firmware.ino` in Arduino IDE.
2. Select **NodeMCU 1.0 (ESP-12E Module)**.
3. Connect NodeMCU via USB and click **Upload**.
4. Verify Serial Monitor outputs: `[WIFI] Access Point Started: AutonomousCar_AP`.

### 2. Install the Android App
1. Open `android-app/` in Android Studio.
2. Connect your **Samsung Galaxy A36 5G** with USB Debugging enabled.
3. Click **Run** (`Shift+F10`).
4. Connect phone Wi-Fi to **`AutonomousCar_AP`** (Password: `car12345678`).

### 3. Connect the Cosmic Byte Ares Pro Controller
1. Turn on gamepad by pressing **[HOME] + [A]** for 3 seconds (Android HID pairing mode).
2. Connect to the controller in the phone's Bluetooth settings.
3. Open the app: Press **Button A** for Manual Mode, **Button B** for Autonomous Mode, or **Button X** for Emergency Stop.

### 4. Run Automated Software Verification
```bash
python tests/run_all_tests.py
```

---

## 📚 Comprehensive Documentation Suite

| Guide | Title | Purpose |
| :---: | :--- | :--- |
| **01** | [`01_SYSTEM_ARCHITECTURE.md`](docs/01_SYSTEM_ARCHITECTURE.md) | High-level architecture, separation of concerns, and data flows |
| **02** | [`02_HARDWARE_SPECIFICATIONS.md`](docs/02_HARDWARE_SPECIFICATIONS.md) | Full datasheets: Samsung A36 5G, NodeMCU, TB6612, TT motors |
| **03** | [`03_COMPONENT_SELECTION_GUIDE.md`](docs/03_COMPONENT_SELECTION_GUIDE.md) | Engineering trade-offs (TB6612 vs L298N, Buck vs 7805) |
| **04** | [`04_COMPLETE_WIRING_DIAGRAM.md`](docs/04_COMPLETE_WIRING_DIAGRAM.md) | Pin-by-pin interconnect table, boot strapping, common ground |
| **05** | [`05_POWER_DISTRIBUTION_AND_BUCK_CONVERTER.md`](docs/05_POWER_DISTRIBUTION_AND_BUCK_CONVERTER.md) | Dual-rail power routing and 5.15V LM2596 calibration |
| **06** | [`06_BATTERY_SELECTION_AND_SAFETY.md`](docs/06_BATTERY_SELECTION_AND_SAFETY.md) | 2S 18650 Li-ion pack, 2S BMS protection, CC/CV charging |
| **07** | [`07_SOFTWARE_ENVIRONMENT_SETUP.md`](docs/07_SOFTWARE_ENVIRONMENT_SETUP.md) | Android Studio, PlatformIO, Arduino IDE, ADB setup |
| **08** | [`08_PYTHON_DEVELOPMENT_ENVIRONMENT.md`](docs/08_PYTHON_DEVELOPMENT_ENVIRONMENT.md) | Virtualenv, PyTorch, Ultralytics, OpenCV installation |
| **09** | [`09_DATASET_PREPARATION_AND_CONVERSION.md`](docs/09_DATASET_PREPARATION_AND_CONVERSION.md) | 6,000 image dataset and YOLO to COCO conversion tool |
| **10** | [`10_MODEL_TRAINING_AND_BENCHMARKING.md`](docs/10_MODEL_TRAINING_AND_BENCHMARKING.md) | Training pipeline and benchmark comparison across 6 models |
| **11** | [`11_MODEL_QUANTIZATION_AND_EXPORT.md`](docs/11_MODEL_QUANTIZATION_AND_EXPORT.md) | ONNX & TFLite export, INT8 and FP16 quantization |
| **12** | [`12_ANDROID_APP_ARCHITECTURE.md`](docs/12_ANDROID_APP_ARCHITECTURE.md) | Kotlin architecture, CameraX non-blocking stream, HUD overlay |
| **13** | [`13_ANDROID_STUDIO_BUILD_AND_INSTALL.md`](docs/13_ANDROID_STUDIO_BUILD_AND_INSTALL.md) | Building APK, Gradle wrapper, runtime permissions |
| **14** | [`14_COSMIC_BYTE_ARES_PRO_SETUP.md`](docs/14_COSMIC_BYTE_ARES_PRO_SETUP.md) | Bluetooth pairing, axis mapping, deadzone tuning, HUD |
| **15** | [`15_ESP8266_FIRMWARE_AND_PIN_BOOT_SAFETY.md`](docs/15_ESP8266_FIRMWARE_AND_PIN_BOOT_SAFETY.md) | Safe boot strap pins (GPIO15, GPIO0), 1000ms watchdog |
| **16** | [`16_WIFI_AP_AND_UDP_COMMUNICATION.md`](docs/16_WIFI_AP_AND_UDP_COMMUNICATION.md) | SoftAP configuration, UDP Port 8888, dual protocol packets |
| **17** | [`17_DUAL_MODE_CONTROL_AND_SAFETY_ARBITRATION.md`](docs/17_DUAL_MODE_CONTROL_AND_SAFETY_ARBITRATION.md) | FSM arbitration, single control owner, disconnect safety |
| **18** | [`18_MOTOR_CALIBRATION_AND_DIFFERENTIAL_TUNING.md`](docs/18_MOTOR_CALIBRATION_AND_DIFFERENTIAL_TUNING.md) | S-curve smoothing, straight-line trim, skid-steer math |
| **19** | [`19_FIELD_TESTING_AND_VERIFICATION_PROCEDURE.md`](docs/19_FIELD_TESTING_AND_VERIFICATION_PROCEDURE.md) | Pre-flight checklist, teleoperation and sign tests |
| **20** | [`20_TROUBLESHOOTING_AND_DIAGNOSTICS.md`](docs/20_TROUBLESHOOTING_AND_DIAGNOSTICS.md) | Comprehensive symptom triage matrix, serial monitor |

---

## 📜 Audit & Verification Reports

- **[`PROJECT_AUDIT.md`](PROJECT_AUDIT.md):** Complete codebase, firmware, dependencies, and security audit.
- **[`EXISTING_IMPLEMENTATION_REPORT.md`](EXISTING_IMPLEMENTATION_REPORT.md):** Baseline capabilities vs. target profile.
- **[`DATASET_AUDIT.md`](DATASET_AUDIT.md):** Exhaustive dataset audit (6,000 images, 6 classes, bounding box sanity).
- **[`MODEL_COMPARISON_PLAN.md`](MODEL_COMPARISON_PLAN.md):** Architectural evaluation plan beyond YOLO.
- **[`MODEL_SELECTION_REPORT.md`](MODEL_SELECTION_REPORT.md):** Empirical benchmark results and primary selection justification.
- **[`FILE_CLEANUP_REPORT.md`](FILE_CLEANUP_REPORT.md):** File inventory, safety backups, and reorganization log.
- **[`MISSING_FEATURES.md`](MISSING_FEATURES.md):** Gap analysis and mitigation strategies.
- **[`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md):** 8-phase execution timeline and milestones.
- **[`FINAL_DELIVERY_CHECKLIST.md`](FINAL_DELIVERY_CHECKLIST.md):** Comprehensive delivery sign-off checklist.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
