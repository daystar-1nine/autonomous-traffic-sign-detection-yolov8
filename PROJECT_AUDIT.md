# PROJECT AUDIT REPORT
**Autonomous AI Traffic Sign Detection & Dual-Mode Robotic Vehicle**
**Primary AI Hardware Profile:** Samsung Galaxy A36 5G (Qualcomm Snapdragon 6 Gen 3, 8GB RAM, Adreno 710 GPU, Hexagon NPU)
**Embedded Hardware Profile:** NodeMCU ESP8266 (ESP-12E) + TB6612FNG Dual H-Bridge + 2× TT DC Motors
**Manual Controller Profile:** Cosmic Byte Ares Pro Wireless Gamepad (Bluetooth HID)
**Audit Date:** 2026-11-06 | **Auditor:** Senior AI/ML, Embedded Systems & Robotics Architect

---

## 1. Executive Summary

This audit establishes the baseline status of the Autonomous AI Traffic Sign Detection Car prior to architecture consolidation, model benchmark beyond YOLO, and deployment to the **Samsung Galaxy A36 5G** mobile platform.

The system is designed with a strict physical and computational separation of concerns:
1. **Perception & Brain Layer (Samsung Galaxy A36 5G):** Captures high-frame-rate road video via CameraX (60/30 FPS), performs object detection and bounding box regression locally via deep neural network inference (LiteRT / TFLite / ONNX Runtime Mobile), processes driving logic (state debouncing, persistence filtering), and interfaces with the Cosmic Byte Ares Pro gamepad over Bluetooth HID.
2. **Execution & Actuation Layer (NodeMCU ESP8266 + TB6612FNG):** Operates as a real-time motor controller over a low-latency 2.4 GHz Wi-Fi UDP link (Port 8888). Manages differential PWM, direction gating, standby switching, and a strict 1000 ms hardware safety watchdog. **The ESP8266 performs zero AI inference.**
3. **Control Arbitration Layer (ControlModeManager):** Guarantees mutual exclusion between Manual Mode (gamepad control), Autonomous Mode (vision inference control), and Emergency Stop (failsafe hardware braking).

---

## 2. Hardware Profile & Validation

### 2.1 AI Processing Brain: Samsung Galaxy A36 5G
- **SoC:** Qualcomm Snapdragon 6 Gen 3 (4nm process, Octa-core: 4× 2.40 GHz Cortex-A78 + 4× 1.80 GHz Cortex-A55).
- **GPU:** Qualcomm Adreno 710 (OpenGL ES 3.2, Vulkan 1.3, OpenCL 2.0).
- **NPU / DSP:** Qualcomm Hexagon NPU with Vector eXtensions (HVX) supporting INT8 and FP16 hardware acceleration via Android NNAPI / Qualcomm QNN runtime.
- **RAM / Storage:** 8 GB LPDDR4X / 128 GB UFS 2.2.
- **Vision Subsystem:** Rear main camera with Optical Image Stabilization (OIS) and autofocus, capable of 1080p@60fps and 4K@30fps.
- **Connectivity:** Wi-Fi 6 (802.11ax/ac/b/g/n, 2.4 GHz + 5 GHz dual band), Bluetooth 5.3 (LE, A2DP, HID profile).
- **Thermal Envelope:** Designed for sustained thermal dissipation up to ~4.5W continuous load.

### 2.2 Robotic Chassis & Actuation Subsystem
- **Microcontroller:** NodeMCU ESP8266 (ESP-12E module, Tensilica Xtensa 32-bit LX106 @ 80/160 MHz, 80 KB RAM, 4 MB Flash).
- **Motor Driver:** TB6612FNG Dual H-Bridge MOSFET driver (peak 3.2A, continuous 1.2A per channel; power-efficient with <0.5V internal drop compared to the legacy L298N's ~2.0V drop).
- **Actuators:** 2× TT DC Geared Motors (1:48 gear ratio, operating voltage 3V–6V, no-load current ~70 mA, stall current ~800 mA at 6V).
- **Power Conversion:** LM2596 DC-DC step-down buck converter (high efficiency switching regulator set to 5.15V DC output, continuous 2.0A, peak 3.0A).
- **Power Source:** 2S Li-ion Battery Pack (7.4V nominal, 8.4V peak fully charged, 18650 cells with integrated 2S BMS protection board).
- **Controller:** Cosmic Byte Ares Pro wireless gamepad operating in Bluetooth HID gamepad mode (X-Input / D-Input Android standard).

---

## 3. Comprehensive Codebase Inventory

| Module Path | Primary Language / Type | Size / Artifacts | Status & Health |
| :--- | :--- | :--- | :--- |
| `01_DOCUMENTATION/` | Markdown (`.md`) | 22 comprehensive guides | Active & up-to-date; requires alignment with Samsung A36 5G specs and non-YOLO benchmarks |
| `02_AI_MODEL/` | Python, Jupyter, Weights | `best_yolov8n.pt` (6.2 MB), `best_yolov8s.pt` (21.5 MB), `yolov8n_traffic_signs.onnx` (12.2 MB), training notebook | Operational; YOLOv8n achieves 99.5% mAP50 on test set. Evaluation of non-YOLO models pending |
| `03_ANDROID_APP/` | Kotlin, Gradle, XML | Complete native project, CameraX, Ares Pro gamepad input, ONNX runtime, HUD UI | Fully functional; requires LiteRT / TFLite runtime backend integration alongside ONNX |
| `04_ESP8266_FIRMWARE/` | C++ / Arduino (`.ino`, `.h`, `.cpp`) | PlatformIO + Arduino IDE firmware, dual-mode UDP handler, watchdog | Verified safe pinout (D1, D2, D5, D6, D7, D8); 1000ms timeout watchdog implemented |
| `05_PYTHON_TOOLS/` | Python 3.14 | Prediction tools, PC telemetry HUD, dataset validator, UDP test clients | Functional; all scripts verified |
| `06_TESTING/` | Python Unit / Mock Tests | 5 test suites (differential drive, mode manager, UDP protocol, decision, model) | 100% tests passing |
| `07_REPORTS/` | JSON, PNG, MP4 | Confusion matrices, PR curves, F1 curves, detection samples, test metrics | Detailed benchmark artifacts present |
| `dataset/` | Images & Annotations | 6,000 images (4200 train, 1200 val, 600 test), 6 traffic sign classes | Balanced, verified, zero corrupted labels |
| `_archive/` | Legacy & Backup files | `Autonomous-Car.zip` (745 MB), legacy scripts, obsolete weight checkpoints | Safely isolated; not part of active build |
| `_backup_pre_dual_mode/` | Backup Snapshot | Pre-dual mode Android and firmware snapshot | Safety fallback preserved |

---

## 4. Architectural Analysis: Dual-Mode Operation

```
+-----------------------------------------------------------------------------------+
|                           SAMSUNG GALAXY A36 5G                                    |
|                                                                                   |
|  [ CameraX 60 FPS ]               [ Cosmic Byte Ares Pro Gamepad ]                |
|          |                                       | (Bluetooth HID)                |
|          v                                       v                                |
|  [ Neural Inference Engine ]             [ AresProController ]                    |
|  (LiteRT / TFLite / ONNX)                        | (Axis X/Y, Triggers, D-Pad)    |
|          |                                       v                                |
|          v                               [ DifferentialDriveController ]          |
|  [ DecisionEngine ]                              | (Smooth Ramping, Deadband)     |
|  (Temporal Filter / Confidence)                  v                                |
|          |                               [ Manual Command Generator ]             |
|          |                                       |                                |
|          +-----------------------+---------------+                                |
|                                  v                                                |
|                      [ ControlModeManager ]                                       |
|             (MANUAL / AUTONOMOUS / EMERGENCY_STOP)                                |
|                                  |                                                |
|                                  v                                                |
|                      [ UdpVehicleClient ]                                         |
|                 (UDP Port 8888, Non-blocking)                                     |
+----------------------------------|------------------------------------------------+
                                   | Wi-Fi 2.4 GHz UDP Packets
                                   v
+-----------------------------------------------------------------------------------+
|                             NODEMCU ESP8266                                       |
|                                                                                   |
|  [ Wi-Fi UDP Receiver: Port 8888 ]                                                |
|          |                                                                        |
|          +--> [ Command Packet Parser ]                                           |
|          |         |-- "CMD:DRIVE:<leftPwm>:<rightPwm>:<seq>"                     |
|          |         +-- "CMD:<ACTION>" (FORWARD, STOP, LEFT, RIGHT, SLOW, FAST)    |
|          |                                                                        |
|          +--> [ 1000ms Safety Watchdog ] ---> [ Auto-Brake on Packet Loss ]       |
|          |                                                                        |
|          v                                                                        |
|  [ TB6612FNG Motor Driver Interface ]                                             |
|  (PWMA: D1, AIN1: D2, AIN2: D5, PWMB: D6, BIN1: D7, BIN2: D8, STBY: 3.3V)         |
|          |                                                                        |
|          +-------------------+--------------------+                               |
|                              |                    |                               |
|                              v                    v                               |
|                      [ Left TT Motor ]    [ Right TT Motor ]                      |
+-----------------------------------------------------------------------------------+
```

---

## 5. Security & Safety Evaluation

1. **Watchdog Failsafe:** The ESP8266 firmware resets motor PWM outputs to 0 and engages high-side active braking if no valid UDP control packet arrives within **1,000 milliseconds**.
2. **Boot-Strap Pin Protection:** On the ESP8266, GPIO0 (D3) and GPIO2 (D4) determine boot mode. Pulling them low prevents flashing or causes boot failure. GPIO15 (D8) must be pulled down for normal flash boot. The motor driver configuration strictly avoids assigning pull-sensitive pins to signals that could pull them to illegal states during power-up.
3. **Controller Disconnection Failsafe:** When the Cosmic Byte Ares Pro gamepad disconnects or goes out of Bluetooth range, `AresProController` detects `ACTION_DISCONNECTED` and immediately issues a zero-velocity emergency stop packet, preventing runaway vehicle behavior.
4. **Air-Gapped Operation:** All communication takes place strictly over a local, offline Wi-Fi access point created by the phone (or a portable local router). No telemetry or video stream leaves the vehicle.

---

## 6. Audit Conclusion & Next Actions

The existing codebase is structurally sound, stable, and tested. The primary upgrade requirements for the Samsung Galaxy A36 5G deployment are:
1. Conduct a rigorous, empirical multi-architecture model comparison beyond YOLO (testing EfficientDet-Lite0, SSD MobileNetV2, NanoDet, PP-PicoDet, RT-DETR vs YOLOv8n).
2. Implement a COCO format dataset exporter (`yolo_to_coco.py`) for reproducible training across non-YOLO toolkits.
3. Integrate LiteRT / TFLite hardware-delegated inference in the Android application alongside ONNX Runtime Mobile.
4. Restructure the repository into the standard modular layout (`android-app/`, `esp8266-firmware/`, `ai-training/`, `models/`, `dataset/`, `tests/`, `docs/`, `scripts/`).
5. Author all 20 required production documentation guides.
