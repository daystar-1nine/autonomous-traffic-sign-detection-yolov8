# IMPLEMENTATION ROADMAP & EXECUTION PLAN
**Autonomous AI Traffic Sign Detection Car — Deployment on Samsung Galaxy A36 5G**
**Hardware Profile:** Samsung Galaxy A36 5G + NodeMCU ESP8266 + Cosmic Byte Ares Pro
**Roadmap Date:** 2026-11-06 | **Lead:** Senior AI/ML & Embedded Systems Architect

---

## 1. Roadmap Overview & Strategic Objectives

This document establishes the step-by-step phased execution plan to transform the existing codebase into a production-grade, fully documented, dual-mode autonomous robotic car system.

```
+-----------------------------------------------------------------------------------+
|                            8-PHASE EXECUTION TIMELINE                             |
|                                                                                   |
|  [Phase 1] Audit & Reports (COMPLETED)                                            |
|       |                                                                           |
|  [Phase 2] Safe Pre-Cleanup Backup & Transient File Cleanup                       |
|       |                                                                           |
|  [Phase 3] Beyond-YOLO Model Benchmarking, COCO Exporter & Model Delivery        |
|       |                                                                           |
|  [Phase 4] Android App Optimization (LiteRT / TFLite + Ares Pro Diagnostic HUD)  |
|       |                                                                           |
|  [Phase 5] ESP8266 Firmware Failsafe Validation & Heartbeat Return               |
|       |                                                                           |
|  [Phase 6] Directory Restructuring to Section 13 Layout                           |
|       |                                                                           |
|  [Phase 7] Comprehensive 20-Guide Documentation Suite Generation                  |
|       |                                                                           |
|  [Phase 8] Automated Verification Testing & Git Repository Synchronization        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Phase-by-Phase Detailed Task Breakdown

### Phase 1: Complete Project Audit & Initial Reports (Status: COMPLETED)
- [x] Recursive codebase and environment inspection.
- [x] Dataset audit and class balance validation (6,000 images, 6 classes, exact parity).
- [x] Hardware profiling for Samsung Galaxy A36 5G (Snapdragon 6 Gen 3) and ESP8266 + TB6612FNG.
- [x] Generate initial 7 audit reports:
  1. `PROJECT_AUDIT.md`
  2. `EXISTING_IMPLEMENTATION_REPORT.md`
  3. `DATASET_AUDIT.md`
  4. `MODEL_COMPARISON_PLAN.md`
  5. `FILE_CLEANUP_REPORT.md`
  6. `MISSING_FEATURES.md`
  7. `IMPLEMENTATION_ROADMAP.md`

---

### Phase 2: Safe Pre-Cleanup Backup & File Cleanup
- [ ] Create timestamped snapshot directory: `_backup_pre_cleanup_20261106/`.
- [ ] Safely purge transient files (`__pycache__/`, `*.pyc`, stale `.cache` files).
- [ ] Verify zero data loss of datasets, model weights, firmware source, and test scripts.

---

### Phase 3: AI Model Comparison, Selection Beyond YOLO & Model Delivery
- [ ] Implement `yolo_to_coco.py` converter script in `ai-training/dataset-tools/` to allow seamless COCO-format evaluation.
- [ ] Implement multi-model benchmark evaluation script comparing:
  - YOLOv8n (baseline)
  - EfficientDet-Lite0
  - SSD MobileNetV2
  - NanoDet-Plus
  - PP-PicoDet-S
  - RT-DETR-Tiny
- [ ] Evaluate parameters, FLOPs, mAP50, mAP50-95, memory footprint, and projected Snapdragon 6 Gen 3 latency.
- [ ] Export production models:
  - Selected best model in TFLite (FP16 and INT8 quantized with metadata)
  - Selected best model in ONNX format
- [ ] Generate `MODEL_SELECTION_REPORT.md` documenting empirical benchmark results.

---

### Phase 4: Android App Optimization (Samsung Galaxy A36 5G)
- [ ] Add Google LiteRT / TFLite interpreter support with GPU / NNAPI delegate fallback alongside ONNX Runtime.
- [ ] Optimize CameraX latest-frame pipeline for Snapdragon 6 Gen 3 (zero buffer copy, 30+ FPS sustained).
- [ ] Enhance Cockpit HUD with real-time Gamepad Diagnostics Overlay (stick deflection vectors, trigger positions, profile indicator).
- [ ] Verify `ControlModeManager` mutual exclusion: `MANUAL` (Ares Pro), `AUTONOMOUS` (AI inference), and `EMERGENCY_STOP`.

---

### Phase 5: ESP8266 Firmware Validation & Bidirectional Telemetry
- [ ] Audit pin configuration to guarantee safe boot states (GPIO0, GPIO2, GPIO15).
- [ ] Verify TB6612FNG 10-bit PWM motor driving logic (`CMD:DRIVE:<leftPwm>:<rightPwm>:<seq>`).
- [ ] Verify backward-compatible autonomous actions (`CMD:FORWARD`, `CMD:STOP`, `CMD:LEFT`, `CMD:RIGHT`, etc.).
- [ ] Verify strict 1000 ms safety watchdog timeout.
- [ ] Add bidirectional UDP heartbeat response (`ACK:<seq>:<uptime>`) for real-time link latency tracking.

---

### Phase 6: Final Directory Restructuring (Section 13 Layout)
Migrate the repository cleanly into:
- `android-app/`
- `esp8266-firmware/`
- `ai-training/`
- `models/`
- `dataset/`
- `tests/`
- `docs/`
- `scripts/`
- `requirements.txt`
- `README.md`

---

### Phase 7: Comprehensive 20-Guide Documentation Suite
Author exhaustive, professional engineering guides in `docs/`:
1. `01_SYSTEM_ARCHITECTURE.md`
2. `02_HARDWARE_SPECIFICATIONS.md`
3. `03_COMPONENT_SELECTION_GUIDE.md`
4. `04_COMPLETE_WIRING_DIAGRAM.md`
5. `05_POWER_DISTRIBUTION_AND_BUCK_CONVERTER.md`
6. `06_BATTERY_SELECTION_AND_SAFETY.md`
7. `07_SOFTWARE_ENVIRONMENT_SETUP.md`
8. `08_PYTHON_DEVELOPMENT_ENVIRONMENT.md`
9. `09_DATASET_PREPARATION_AND_CONVERSION.md`
10. `10_MODEL_TRAINING_AND_BENCHMARKING.md`
11. `11_MODEL_QUANTIZATION_AND_EXPORT.md`
12. `12_ANDROID_APP_ARCHITECTURE.md`
13. `13_ANDROID_STUDIO_BUILD_AND_INSTALL.md`
14. `14_COSMIC_BYTE_ARES_PRO_SETUP.md`
15. `15_ESP8266_FIRMWARE_AND_PIN_BOOT_SAFETY.md`
16. `16_WIFI_AP_AND_UDP_COMMUNICATION.md`
17. `17_DUAL_MODE_CONTROL_AND_SAFETY_ARBITRATION.md`
18. `18_MOTOR_CALIBRATION_AND_DIFFERENTIAL_TUNING.md`
19. `19_FIELD_TESTING_AND_VERIFICATION_PROCEDURE.md`
20. `20_TROUBLESHOOTING_AND_DIAGNOSTICS.md`
Along with root `README.md` and `FINAL_DELIVERY_CHECKLIST.md`.

---

### Phase 8: Software Testing & Git Repository Synchronization
- [ ] Run complete automated software test suite across controller, protocol, decision, and model modules.
- [ ] Verify 100% test pass rate.
- [ ] Stage all changes, commit with clean semantic messages, and push to GitHub remote repository.

---

## 3. Milestones & Quality Gates

| Milestone | Criterion for Passing | Verification Tool |
| :--- | :--- | :--- |
| **M1: Audit Complete** | All 7 initial audit reports generated and validated | Inspection |
| **M2: Safe Backup & Cleanup** | Snapshot created, zero loss of core data | Directory diff |
| **M3: Model Comparison & Selection** | Benchmark table across 6 architectures, COCO tool ready, best model exported | Python benchmark harness |
| **M4: Android App Optimized** | LiteRT support integrated, Ares Pro HUD active | Unit & UI tests |
| **M5: Firmware Safety Verified** | Pin boot safety and 1000ms watchdog validated | Unit & protocol tests |
| **M6: Structure Reorganized** | Clean Section 13 directory layout with 0 broken links | Directory validation |
| **M7: 20 Guides Complete** | All 20 technical guides generated in `docs/` | Markdown audit |
| **M8: Final Git Sync** | 100% tests passing, clean tree pushed to remote | `git status` / `git push` |
