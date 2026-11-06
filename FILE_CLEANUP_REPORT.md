# FILE CLEANUP & REORGANIZATION REPORT
**Autonomous AI Traffic Sign Detection Car**
**Audit Date:** 2026-11-06 | **Lead:** Senior AI/ML & Embedded Systems Architect

---

## 1. Executive Summary

This report establishes the file cleanup and restructuring plan for the project. Before performing any file modifications or relocations, every file in the repository was indexed and classified to ensure zero loss of valuable datasets, trained weights, firmware implementations, or test suites.

A **timestamped safety backup** (`_backup_pre_cleanup_<timestamp>/`) will be generated prior to deleting transient caches or moving directories to the final standard structure.

---

## 2. File Inventory & Categorization

### 2.1 Category A: Core Production Files (MUST PRESERVE)
These files represent active, production-grade components that are retained, migrated, and maintained:
- **Dataset (`dataset/`):**
  - `dataset/train/` (4,200 images + 4,200 labels)
  - `dataset/valid/` (1,200 images + 1,200 labels)
  - `dataset/test/` (600 images + 600 labels)
  - `dataset/data.yaml` & `dataset/classes.txt`
- **Active AI Models & Weights (`02_AI_MODEL/weights/`):**
  - `best_yolov8n.pt` (6.2 MB) — primary production model.
  - `best_yolov8s.pt` (21.5 MB) — high-accuracy validation model.
  - `yolov8n_traffic_signs.onnx` (12.2 MB) — active export.
- **Android Application Source (`03_ANDROID_APP/`):**
  - `app/src/main/java/com/autonomous/aicontrol/`: All Kotlin classes (`MainActivity`, `AresProController`, `DifferentialDriveController`, `ControlModeManager`, `YoloDetector`, `DecisionEngine`, `UdpVehicleClient`, `OverlayView`).
  - `app/src/main/res/`: Layouts, drawables, strings, themes.
  - `app/src/main/AndroidManifest.xml`, `build.gradle`, `settings.gradle`.
  - `app/src/main/assets/`: Model runtime assets.
- **ESP8266 Firmware (`04_ESP8266_FIRMWARE/`):**
  - `esp8266_firmware.ino`, `src/main.cpp`.
  - `include/motor_driver.h`, `include/pin_config.h`, `include/udp_protocol.h`, `include/watchdog.h`.
  - `platformio.ini`.
- **Automated Test Suites (`06_TESTING/`):**
  - `test_differential_drive.py`, `test_mode_manager.py`, `test_udp_drive_packet.py`, `test_decision_engine.py`, `test_model_inference.py`.
- **Python Utility Scripts (`05_PYTHON_TOOLS/`):**
  - `predict_image.py`, `predict_video.py`, `webcam.py`, `validate_dataset.py`, `pc_telemetry_hud.py`, `utils.py`.

### 2.2 Category B: Redundant & Duplicate Files (SAFE TO CONSOLIDATE)
These files duplicate existing files or are redundant copies:
- `03_ANDROID_APP/models/yolov8n.onnx`: Redundant duplicate of `03_ANDROID_APP/app/src/main/assets/yolov8n.onnx` and `02_AI_MODEL/exports/yolov8n_traffic_signs.onnx`. (Consolidate into central `models/` directory).
- `_archive/legacy_models/best_yolov8n_backup.pt`: Identical MD5 hash to `02_AI_MODEL/weights/best_yolov8n.pt`.
- `_archive/legacy_models/best.pt`: Identical to `best_yolov8s.pt`.
- `02_AI_MODEL/scripts/__pycache__/` & `05_PYTHON_TOOLS/scripts/__pycache__/`: Transient compiled bytecode. (Delete safely).
- `dataset/*/*.cache`: YOLO label cache files. (Can be safely cleared or regenerated on demand).

### 2.3 Category C: Historical Archives (PRESERVE IN ARCHIVE)
- `_archive/Autonomous-Car.zip` (745 MB): Large historical zip containing initial raw project files. Preserved safely in `_archive/` or excluded from Git tracking via `.gitignore` to prevent repository bloat.
- `_archive/legacy_src/`: Early monolithic scripts. Preserved for provenance.
- `_backup_pre_dual_mode/`: Snapshot prior to dual-mode controller integration. Preserved.

---

## 3. Safe Cleanup & Migration Plan

### Step 1: Pre-Cleanup Backup
Execute an automated snapshot copy of the workspace into `_backup_pre_cleanup_20261106/`.

### Step 2: Remove Purely Transient Files
Delete:
- `__pycache__/` directories
- `*.pyc` files
- Intermediate temporary export logs

### Step 3: Migration to Final Standard Directory Layout (Section 13)
The project structure will be organized cleanly into:

```
├── android-app/             <-- Migrated from 03_ANDROID_APP
│   ├── app/
│   │   ├── src/main/assets/ (models, labels)
│   │   ├── src/main/java/com/autonomous/aicontrol/
│   │   └── src/main/res/
│   ├── build.gradle
│   └── settings.gradle
│
├── esp8266-firmware/        <-- Migrated from 04_ESP8266_FIRMWARE
│   ├── esp8266_firmware.ino
│   ├── include/
│   ├── src/
│   └── platformio.ini
│
├── ai-training/             <-- Migrated from 02_AI_MODEL
│   ├── dataset-tools/       <-- Includes yolo_to_coco.py
│   ├── notebooks/
│   ├── scripts/
│   └── requirements.txt
│
├── models/                  <-- Consolidated model registry
│   ├── exported/            <-- .tflite, .onnx
│   └── weights/             <-- best_yolov8n.pt, best_yolov8s.pt
│
├── dataset/                 <-- Maintained intact (train, valid, test, data.yaml)
│   ├── train/
│   ├── valid/
│   ├── test/
│   └── data.yaml
│
├── tests/                   <-- Migrated from 06_TESTING
│   ├── communication/
│   ├── controller/
│   ├── decision/
│   └── model/
│
├── docs/                    <-- Migrated & expanded 20 documentation guides
│   ├── 01_SYSTEM_ARCHITECTURE.md
│   ├── 02_HARDWARE_SPECIFICATION.md
│   ├── 03_COMPLETE_WIRING_GUIDE.md
│   ├── ... (All 20 comprehensive guides)
│
├── scripts/                 <-- Migrated from 05_PYTHON_TOOLS
│   ├── pc_telemetry_hud.py
│   ├── predict_image.py
│   ├── predict_video.py
│   └── validate_dataset.py
│
├── requirements.txt         <-- Consolidated dependencies
└── README.md                <-- Root project README
```

---

## 4. Verification Check After Restructuring

Following restructuring, the automated test harness will be executed from the new locations to verify:
- [x] All 5 unit test suites pass from `tests/`.
- [x] Python tools execute cleanly from `scripts/`.
- [x] Android app builds and recognizes models from `android-app/app/src/main/assets/`.
- [x] ESP8266 firmware builds cleanly from `esp8266-firmware/`.
