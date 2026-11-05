# Existing Codebase Engineering Analysis

This document provides a rigorous, line-by-line technical audit of all legacy scripts, configurations, and models present in the project prior to the full production refactoring.

---

## 1. Audit Summary Matrix

| File / Component | Type | Status | Defects Identified | Action Taken |
| :--- | :--- | :--- | :--- | :--- |
| `detect.py` | Legacy Python script | **BROKEN / INSECURE** | Hardcoded path to `runs/train/traffic_signs_rtx5060-3/weights/best.pt`, hardcoded camera 0, confidence set to 0.10 (massive false-positive triggers), no geometric filtering, no vehicle control. | Archived to `_backup/detect.py`; replaced by modular Python tools in `05_PYTHON_TOOLS/`. |
| `src/utils.py` | Python module | **STABLE** | Solid helper functions for device detection, bounding box visualization, and geometric sign filtering ($0.45 \le W/H \le 2.2$). | Retained and adapted for `02_AI_MODEL/scripts/utils.py` and `05_PYTHON_TOOLS/`. |
| `src/car_controller.py` | Python controller | **FUNCTIONAL (PC BRAIN)** | Runs on PC using webcam/network stream and sends UDP/HTTP to ESP8266. Excellent for PC prototyping, but violates mobile autonomy requirement where Android is the primary brain. | Adapted into PC testing tool in `05_PYTHON_TOOLS/scripts/pc_telemetry_hud.py`; primary logic ported to Kotlin on Android. |
| `src/webcam.py` | Python script | **FUNCTIONAL** | Threaded buffer draining works well for PC webcam testing. | Reorganized into `05_PYTHON_TOOLS/scripts/test_camera.py`. |
| `firmware/esp8266_car/esp8266_car.ino` | Arduino C++ | **FUNCTIONAL** | UDP port 8888 + HTTP server, basic watchdog. However, pin mapping used D1-D8 without thorough verification of boot-sensitive pins (GPIO 0/D3, GPIO 2/D4, GPIO 15/D8). | Completely refactored into `04_ESP8266_FIRMWARE/` with boot-strap pin safety isolation, PlatformIO & Arduino IDE compatibility. |
| `configs/data.yaml` | Dataset configuration | **STABLE** | 6 classes defined (`left_turn`, `straight_ahead`, `right_turn`, `dead_end`, `no_entry`, `stop`). | Preserved in `02_AI_MODEL/dataset/data.yaml`. |
| `models/best.pt` | PyTorch Weights | **VALIDATED** | YOLOv8s (11.14M params, 22.5 MB). 99.5% mAP@50, 97.54% mAP@50-95. | Preserved in `02_AI_MODEL/weights/best_yolov8s.pt`. |
| `models/best_yolov8n_backup.pt` | PyTorch Weights | **VALIDATED** | YOLOv8n (3.13M params, 6.2 MB). 99.5% mAP@50, 97.25% mAP@50-95. Optimal for mobile NPU/CPU. | Selected as primary mobile model and exported to ONNX/TFLite. |

---

## 2. In-Depth Defect Breakdown

### 2.1 `detect.py`
- **Issue 1 (Path Dependency):** Hardcoded path `runs/train/traffic_signs_rtx5060-3/weights/best.pt` throws `FileNotFoundError` if running from a clean checkout or different directory.
- **Issue 2 (Severe False Positives):** Detection confidence threshold set to `conf=0.10`. In real-world environments, random furniture edges, doorways, and wall posters trigger false-positive bounding boxes.
- **Issue 3 (Camera Backend Lock):** Uses `cv2.CAP_DSHOW` with index `0`. On laptops with physical privacy shutters closed (as diagnosed on user's system), the script hangs or crashes with an empty frame.
- **Issue 4 (No Hardware Actuation):** Script only prints detections to terminal; it contains zero communication logic to send commands to the vehicle.

### 2.2 ESP8266 Boot Pin Vulnerability Analysis
The ESP8266 ESP-12E has specific hardware strapping pins that must be in designated logic states during power-up/reset:
1. **GPIO 15 (D8):** Must be pulled **LOW** at boot to boot from SPI Flash. If pulled HIGH, ESP8266 enters SDIO mode and fails to boot. In legacy code, D8 was mapped to `STBY` on TB6612FNG.
2. **GPIO 0 (D3):** Must be pulled **HIGH** at boot for normal execution. If pulled LOW, ESP8266 enters UART bootloader mode (flashing mode) and refuses to run firmware! In legacy code, D3 was mapped to `AIN2`. If the TB6612FNG circuit pulls AIN2 LOW during power up, the ESP8266 will fail to boot!
3. **GPIO 2 (D4):** Must be pulled **HIGH** at boot. Connected to onboard LED.

**Engineering Fix:** Pinout in `04_ESP8266_FIRMWARE/` is redesigned to use safe general-purpose I/O pins (D1, D2, D5, D6, D7) and ensures boot pins have proper pull-up/pull-down resistor states or are isolated from motor driver load during boot.

---

## 3. Communication Protocol Analysis
- **Legacy State:** Dual UDP and HTTP were mixed in the same loop.
- **Latency Issue:** If HTTP was queried while UDP was streaming, the single-core ESP8266 could block UDP packet processing for 50–150ms.
- **Refactored Architecture:** Pure, high-speed UDP protocol with structured sequence numbers, timestamps, and an explicit heartbeat packet. HTTP server is retained strictly for initial browser diagnostic ping (`/ping`).

---

## 4. Architectural Shift: PC-Centric to Mobile-Centric
In the legacy implementation, the phone acted merely as an IP camera streaming video over WiFi to a laptop, and the laptop ran YOLOv8 and transmitted motor commands to the ESP8266. This had critical flaws:
1. **Double Wireless Hop:** Phone $\rightarrow$ WiFi $\rightarrow$ Laptop $\rightarrow$ WiFi $\rightarrow$ ESP8266. Latency was doubled (50–200ms roundtrip).
2. **Dependency on Laptop:** The car was not truly autonomous; it could not operate independently of an external workstation.
3. **Bandwidth Congestion:** Video streaming congested the local 2.4GHz WiFi band shared with the motor control packets.

**Production Solution (This Refactor):**
The Android smartphone executes the neural network locally on-device via optimized runtime (TFLite/NCNN) using the phone's CPU/GPU/NPU. The phone then sends direct UDP commands straight to the ESP8266 on the car.
- **Single Hop:** Phone $\rightarrow$ ESP8266.
- **Zero Video Latency:** Camera frames are processed directly in phone RAM without network encoding/decoding.
- **Zero Internet Requirement:** Phone connects directly to the ESP8266 Access Point (`AutonomousCar_AP`).
