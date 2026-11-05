# 🚗 Smartphone-Based AI Autonomous Traffic Sign Detection Car

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-blue?logo=python)](https://www.python.org/)
[![Android](https://img.shields.io/badge/Android-Kotlin%20%7C%20CameraX-3DDC84?logo=android)](03_ANDROID_APP)
[![YOLOv8](https://img.shields.io/badge/Ultralytics-YOLOv8n%20(3.13M)-00FFFF?logo=yolo)](02_AI_MODEL)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![ESP8266](https://img.shields.io/badge/ESP8266-NodeMCU%20v2.0-red?logo=espressif)](04_ESP8266_FIRMWARE)
[![mAP@50](https://img.shields.io/badge/mAP%4050-99.5%25-brightgreen)](07_REPORTS/MODEL_BENCHMARK.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade, complete robotic vehicle system that transforms an **Android smartphone (Redmi)** into the primary on-device artificial intelligence vision system for an autonomous car. Featuring local **YOLOv8n** on-device neural network detection, spatial sign proximity estimation, sub-3ms wireless UDP communication, and NodeMCU ESP8266 dual-motor control with TB6612FNG. Operates **100% locally** without requiring cloud or internet connectivity.

> 🚀 **Ready to Build & Drive?** Follow the step-by-step physical assembly, firmware flashing, and autonomous testing guide: **[`STEPS_TO_COMPLETE.md`](STEPS_TO_COMPLETE.md)**

---

## 📌 Master Architecture & System Highlights

```text
       ┌─────────────────────────────────────────────────────────┐
       │             ON-DEVICE MOBILE AI VISION BRAIN            │
       │           (Android Smartphone on Front Chassis)         │
       │  • CameraX 1080p @ 30 FPS Stream                        │
       │  • YOLOv8n TFLite (3.13M params, ~22ms Mobile Latency)  │
       │  • 6-Stage Spatial & Temporal Decision Engine           │
       │  • Sci-Fi Cockpit Telemetry HUD                         │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼ High-Speed UDP Datagrams (Port 8888, <3ms)
       ┌─────────────────────────────────────────────────────────┐
       │             EMBEDDED ACTUATION CONTROLLER               │
       │               (NodeMCU ESP8266 ESP-12E)                 │
       │  • Private Standalone SoftAP (AutonomousCar_AP)         │
       │  • Non-blocking Command Parser & 1.0s Watchdog Fail-Safe│
       │  • Dynamic Wireless Motor Trim & Soft-PWM Ramp          │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼ MOSFET H-Bridge PWM
       ┌─────────────────────────────────────────────────────────┐
       │              POWER & PROPULSION HARDWARE                │
       │  • TB6612FNG Dual Driver (Zero Voltage Drop, 3.2A peak) │
       │  • 2x TT DC Gearbox Motors (1:48 Differential Drive)    │
       │  • 2S 18650 Li-ion Battery Pack (7.4V Nominal, 3A Fuse) │
       │  • LM2596/Mini360 Buck Converter (Regulated 5.1V Logic) │
       └─────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Directory Structure

```text
AUTONOMOUS_AI_CAR/
│
├── README.md                          # Primary overview & quickstart (this file)
├── STEPS_TO_COMPLETE.md               # 🚀 Master Step-by-Step Physical Assembly & Testing Guide
├── LICENSE                            # MIT Open Source License
├── requirements.txt                   # Root environment dependencies
│
├── 01_DOCUMENTATION/                  # Comprehensive 25-part engineering & architecture guides
│   ├── 01_START_HERE.md               # Beginner's 5-step onboarding guide
│   ├── 02_HARDWARE_REQUIREMENTS.md    # Hardware checklist & specs
│   ├── 03_COMPONENTS.md               # Component deep-dive (NodeMCU, TB6612, TT Motors)
│   ├── 04_COMPLETE_WIRING_GUIDE.md    # 15-point schematic & common GND wiring
│   ├── 05_POWER_DISTRIBUTION.md       # Current budgets & thermal analysis
│   ├── 06_BATTERY_SAFETY.md           # 18650 Li-ion safety & 3A fuse placement
│   ├── 07_SOFTWARE_INSTALLATION.md    # Fresh Windows installation guide
│   ├── 08_PYTHON_SETUP.md             # Virtual environment setup
│   ├── 09_MODEL_TRAINING.md           # YOLOv8 training & evaluation
│   ├── 10_MODEL_EXPORT.md             # ONNX, TFLite (FP16), NCNN export
│   ├── 11_ANDROID_SETUP.md            # Android Studio & Redmi developer settings
│   ├── 12_ANDROID_INSTALLATION.md     # Building & installing APK
│   ├── 13_ESP8266_SETUP.md            # NodeMCU firmware flashing
│   ├── 14_WIFI_SETUP.md               # SoftAP & Station mode configuration
│   ├── 15_COMMUNICATION_PROTOCOL.md   # UDP datagram specification (Port 8888)
│   ├── 16_AUTONOMOUS_MODE.md          # Decision engine states & sign behaviors
│   ├── 17_MANUAL_MODE.md              # Manual WASD controls & Emergency Stop
│   ├── 18_MOTOR_CALIBRATION.md        # Straight-line trim & 90° turn calibration
│   ├── 19_TESTING_GUIDE.md            # Unit, bench & floor track tests
│   ├── 20_TROUBLESHOOTING.md          # Symptom, root-cause & fix matrix
│   ├── 21_FAQ.md                      # Frequently asked questions
│   ├── 22_FINAL_CHECKLIST.md          # Pre-flight sign-off checklist
│   ├── PROJECT_OVERVIEW.md            # System rationale & technical innovations
│   ├── PROJECT_ARCHITECTURE.md        # Three-tier hardware & software architecture
│   └── IMPLEMENTATION_PLAN.md         # Full project execution roadmap
│
├── 02_AI_MODEL/                       # Deep learning models, dataset configs & exports
│   ├── dataset/ (data.yaml, classes)  # Dataset definition and class mappings
│   ├── notebooks/                     # YOLOv8_Traffic_Sign_Detection.ipynb
│   ├── scripts/                       # train.py, evaluate.py, export_model.py, benchmark.py
│   ├── weights/                       # best_yolov8n.pt (Primary Mobile), best_yolov8s.pt
│   ├── exports/                       # yolov8n_traffic_signs.onnx
│   └── requirements.txt
│
├── 03_ANDROID_APP/                    # Native Android Studio Kotlin Project
│   ├── app/src/main/
│   │   ├── AndroidManifest.xml        # Camera & Wi-Fi permissions
│   │   ├── assets/                    # yolov8n_traffic_signs.onnx / tflite models
│   │   ├── java/com/autonomous/aicontrol/
│   │   │   ├── MainActivity.kt        # CameraX binding & lifecycle
│   │   │   ├── ai/                    # YoloDetector.kt (TFLite tensor decoding & NMS)
│   │   │   ├── decision/              # DecisionEngine.kt (Debounce, proximity, cooldown)
│   │   │   ├── network/               # UdpVehicleClient.kt (Non-blocking datagrams)
│   │   │   └── ui/                    # OverlayView.kt (Sci-Fi cockpit HUD)
│   │   └── res/layout/activity_main.xml
│   └── README.md
│
├── 04_ESP8266_FIRMWARE/               # NodeMCU ESP-12E Firmware
│   ├── src/main.cpp                   # PlatformIO modular source
│   ├── include/                       # pin_config.h, motor_driver.h, udp_protocol.h, watchdog.h
│   ├── esp8266_firmware.ino           # Standalone 1-click Arduino IDE sketch
│   ├── platformio.ini                 # PlatformIO configuration
│   └── README.md
│
├── 05_PYTHON_TOOLS/                   # PC Development, Simulation & Diagnostic Suite
│   ├── scripts/                       # predict_image.py, predict_video.py, webcam.py,
│   │                                  # validate_dataset.py, compare_models.py, test_communication.py,
│   │                                  # test_camera.py, test_detection.py, pc_telemetry_hud.py
│   ├── test_images/                   # Sample test images
│   ├── requirements.txt
│   └── README.md
│
├── 06_TESTING/                        # Automated Verification Test Suite
│   ├── model_tests/                   # test_model_inference.py (100% PASS)
│   ├── integration_tests/             # test_decision_engine.py (100% PASS)
│   └── communication_tests/           # test_udp_mock.py (100% PASS)
│
├── 07_REPORTS/                        # Technical Performance & Audit Reports
│   ├── PROJECT_AUDIT.md               # Complete initial technical audit
│   ├── EXISTING_CODE_ANALYSIS.md      # Line-by-line legacy defect analysis
│   ├── MODEL_AUDIT.md                 # Neural network benchmark & tensor specs
│   ├── DEPENDENCY_AUDIT.md            # Python, Arduino & Android environment audit
│   ├── DATASET_AUDIT.md               # Dataset & annotation audit
│   ├── CLEANUP_REPORT.md              # File reorganization & migration record
│   ├── TEST_RESULTS.md                # 15-stage verification & test matrix
│   ├── FINAL_DELIVERY_REPORT.md       # Engineering handover & certification report
│   ├── MODEL_BENCHMARK.md             # Empirical test split accuracy & FLOPs
│   ├── PERFORMANCE_REPORT.md          # 41.8ms end-to-end latency budget
│   ├── FINAL_TEST_REPORT.md           # Engineering verification certification
│   ├── evaluation/                    # Confusion matrices, F1 & PR curves, training logs
│   ├── predictions/                   # Annotated prediction images & JSON summaries
│   └── videos/                        # Annotated demonstration videos
│
├── dataset/                           # Full 6,000-image dataset (train / valid / test)
│   └── sample_signs/                  # High-res sample signs for printing/testing
│
└── _archive/                          # Historical backups & legacy raw materials
```

---

## 🚀 Quickstart: Running in 3 Steps

### Step 1: Flash NodeMCU ESP8266
Open [`04_ESP8266_FIRMWARE/esp8266_firmware.ino`](04_ESP8266_FIRMWARE/esp8266_firmware.ino) in Arduino IDE, select board **NodeMCU 1.0 (ESP-12E)**, and click Upload.

### Step 2: Install Android App
Open [`03_ANDROID_APP`](03_ANDROID_APP) in Android Studio, connect your Redmi phone via USB, and click **Run 'app'**.

### Step 3: Connect & Drive
Connect your phone's Wi-Fi to **`AutonomousCar_AP`** (Password: `car12345678`). Launch the app and tap **AUTO MODE** to start autonomous driving!

For detailed wiring, multimeter voltage calibration, and assembly, read **[`STEPS_TO_COMPLETE.md`](STEPS_TO_COMPLETE.md)** and [`01_DOCUMENTATION/01_START_HERE.md`](01_DOCUMENTATION/01_START_HERE.md).

---

## 🚀 Installation & Local Setup

### 1. Clone or Open Workspace
```bash
cd "S:/Kaushalya 2.0/R with CV"
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 CLI Usage Instructions

### 1. Image Detection (`predict_image.py`)
Run inference on a single image or a directory of images:

```bash
# Predict on a single image
python src/predict_image.py --source dataset/sample_signs/sample_5_stop.jpg --model models/best.pt --conf 0.40

# Predict on all sample images and save to outputs/predictions/
python src/predict_image.py --source dataset/sample_signs/ --model models/best.pt --save-dir outputs/predictions/showcase --conf 0.40

# Display window interactively
python src/predict_image.py --source dataset/sample_signs/sample_0_left_turn.jpg --show
```

### 2. Video Detection (`predict_video.py`)
Process a video file, draw bounding boxes with confidence, overlay telemetry HUD, and output an annotated `.mp4` file:

```bash
python src/predict_video.py --source dataset/demo_traffic_signs.mp4 --model models/best.pt --output outputs/videos/annotated_demo.mp4 --conf 0.45
```

### 3. Real-Time Autonomous Car Controller (`car_controller.py`)
Run the master vehicle brain linking the phone camera feed, GPU YOLOv8s inference, distance proximity engine, and NodeMCU ESP8266 motor telemetry:

```bash
python src/car_controller.py --stream-url "http://192.168.137.1:4747/video" --esp-ip "192.168.137.45" --conf 0.65
```

**Cockpit Controls:**
- `M` : Toggle Autonomous Driving ↔ Manual Keyboard Control
- `SPACE` : Emergency Brake (Instant zero-speed stop)
- `W / A / S / D` : Manual steering control
- `+ / -` : Adjust detection threshold (+/- 0.05)
- Detailed circuit wiring and assembly instructions: [`HARDWARE_SETUP.md`](HARDWARE_SETUP.md).

### 4. Live Webcam & Stream Detection (`webcam.py`)
Launch real-time camera detection for autonomous car testing:

```bash
# Standard integrated laptop webcam (Index 0)
python src/webcam.py --camera-index 0 --conf 0.45

# External USB camera (Index 1)
python src/webcam.py --camera-index 1 --conf 0.45

# IP Camera / DroidCam / RTSP Stream
python src/webcam.py --stream-url "http://192.168.1.100:4747/video" --conf 0.45

# Record live detection stream to an MP4 file
python src/webcam.py --camera-index 0 --record outputs/videos/live_recording.mp4
```

**Interactive Controls During Camera Streaming:**
- `Q` or `ESC` : Quit stream cleanly
- `S` : Save current detection frame snapshot to `outputs/predictions/`
- `+` / `=` : Increase confidence threshold by 0.05
- `-` / `_` : Decrease confidence threshold by 0.05

### 4. Model Evaluation & Benchmarking (`evaluate.py`)
Evaluate `models/best.pt` on the unseen test set or validation set:

```bash
# Evaluate on test split
python src/evaluate.py --split test --data configs/data.yaml --model models/best.pt --name test_split_benchmarks

# Evaluate on validation split
python src/evaluate.py --split val --data configs/data.yaml --model models/best.pt --name val_benchmarks
```

### 5. Model Training (`train.py`)
Train or fine-tune YOLOv8 Nano:

```bash
# Fresh training for 100 epochs
python src/train.py --data configs/data.yaml --epochs 100 --batch 16 --imgsz 640

# Resume interrupted training from last checkpoint
python src/train.py --resume models/last.pt
```

---

## ☁️ Google Colab Execution Guide

For high-speed GPU training on a Tesla T4 / A100 GPU:

1. Open [Google Colab](https://colab.research.google.com/).
2. Upload the notebook [`notebooks/YOLOv8_Traffic_Sign_Detection.ipynb`](notebooks/YOLOv8_Traffic_Sign_Detection.ipynb).
3. Under **Runtime → Change runtime type**, select **T4 GPU** (or A100).
4. Upload `Autonomous-Car.zip` to your Google Drive root directory (`MyDrive/Autonomous-Car.zip`).
5. Run all notebook cells sequentially:
   - **Cells 1–4:** Mounts Drive, unzips dataset to local NVMe, and configures dynamic paths.
   - **Cell 5:** Trains YOLOv8n for 100 epochs, writing weights directly to `/content/drive/MyDrive/YOLOv8_Project/`.
   - **Cell 6:** Runs benchmark validation on the 600 test images.
   - **Cell 7:** Displays training loss curves, PR curves, and confusion matrices.
   - **Cell 8:** Visualizes detections on test images with badges.
   - **Cell 9:** Exports the final model to **ONNX format** for embedded automotive deployment.

---

## 🔮 Future Improvements & Autonomous Vehicle Roadmap

1. **Edge Optimization (TensorRT & OpenVINO):** Convert the trained ONNX model to FP16 TensorRT engines for sub-5ms latency on NVIDIA Jetson Orin Nano.
2. **Vehicle Actuation Integration (ROS2 / CAN Bus):** Connect detection outputs to ROS2 node publishing steering, deceleration, and stop commands over CAN bus.
3. **Adverse Weather Data Augmentation:** Expand dataset with synthetic rain, fog, nighttime glare, and motion blur to ensure robust detection in poor environmental conditions.
4. **Depth Camera Fusion:** Fuse 2D YOLO bounding boxes with Intel RealSense D435i depth maps to estimate exact 3D Euclidean distances to traffic signs.

---

## 📄 License & Attribution

- Built as part of the **Autonomous Car Computer Vision** initiative.
- Dataset based on research: *"Benchmarking YOLOv8 to YOLOv11 Architectures for Real-Time Traffic Sign Recognition in Embedded 1:10 Scale Autonomous Vehicles"*, Technologies (MDPI), 2025.
