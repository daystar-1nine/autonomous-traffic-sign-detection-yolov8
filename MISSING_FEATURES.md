# MISSING FEATURES & GAP ANALYSIS REPORT
**Autonomous AI Traffic Sign Detection Car**
**Target Platforms:** Samsung Galaxy A36 5G + NodeMCU ESP8266 + Cosmic Byte Ares Pro Gamepad
**Report Date:** 2026-11-06 | **Lead:** Senior AI/ML & Embedded Systems Architect

---

## 1. Executive Summary

This report identifies all functional, architectural, operational, and documentation gaps between the current project baseline and a complete, production-ready autonomous driving system deployed on the **Samsung Galaxy A36 5G** with **Cosmic Byte Ares Pro** manual dual-mode control.

Each missing feature is classified by urgency, technical complexity, and mitigation strategy.

---

## 2. Gap Analysis Matrix

| ID | Feature / Capability | Current Status | Target Requirement | Priority | Impact |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **GAP-01** | **Multi-Model Benchmark Beyond YOLO** | Only YOLOv8n and YOLOv8s evaluated | Benchmark EfficientDet-Lite0, SSD MobileNetV2, NanoDet, PP-PicoDet, RT-DETR vs YOLOv8n | **High** | Select best latency/accuracy model for Snapdragon 6 Gen 3 |
| **GAP-02** | **COCO Dataset Converter Utility** | Dataset is exclusively in YOLO format | Implement standalone `yolo_to_coco.py` converter | **High** | Enables training non-YOLO architectures without modifying original data |
| **GAP-03** | **LiteRT / TFLite Android Runtime** | Android app currently uses ONNX Runtime Mobile | Provide LiteRT / TFLite interpreter support with GPU / NNAPI delegates | **High** | Unlocks Snapdragon 6 Gen 3 Adreno 710 GPU & Hexagon NPU acceleration |
| **GAP-04** | **Model Post-Training Quantization (INT8/FP16)** | Only FP32 ONNX export is deployed | Provide INT8 and FP16 quantized TFLite & ONNX models | **High** | 4× reduction in memory bandwidth and 2.5× inference speedup |
| **GAP-05** | **Ares Pro In-App Calibration HUD** | Joystick calibration is hardcoded in Kotlin | Add real-time visual gamepad diagnostic overlay to Cockpit HUD | **Medium** | Visual confirmation of axis deadband, trigger values, and button mapping |
| **GAP-06** | **Watchdog Round-Trip Heartbeat Ping** | ESP8266 watchdog only times out passively | Return UDP ACK packet to Android to track bidirectional link latency | **Medium** | Android HUD displays true live round-trip network ping in ms |
| **GAP-07** | **Standard Modular Directory Structure** | Numbered prefix layout (`01_`, `02_`, etc.) | Restructure to clean standard layout (`android-app/`, `esp8266-firmware/`, etc.) | **High** | Section 13 project layout compliance |
| **GAP-08** | **Comprehensive 20-Guide Documentation** | 22 unstandardized markdown notes | Standardize and generate 20 comprehensive technical guides | **High** | Complete end-to-end operational, electrical, and software documentation |

---

## 3. Deep-Dive: Technical Details of Missing Capabilities

### 3.1 Multi-Architecture Benchmark & Evaluation Tooling (GAP-01 & GAP-02)
- **Problem:** Currently, the system relies exclusively on YOLOv8. While YOLOv8n offers state-of-the-art mAP, lightweight alternatives such as EfficientDet-Lite0 and NanoDet-Plus operate at significantly lower computational complexity (GFLOPs < 2.5 vs 8.7), which may provide superior thermal stability on mobile devices during prolonged drives.
- **Solution:**
  1. Author a high-performance `yolo_to_coco.py` script that maps the 6,000 images and YOLO labels into standardized `instances_train.json`, `instances_val.json`, and `instances_test.json`.
  2. Implement an empirical benchmark comparison script evaluating parameters, FLOPs, mAP50, mAP50-95, model size, and projected Snapdragon 6 Gen 3 latency across all candidate models.
  3. Export the selected best model with metadata into `models/exported/`.

### 3.2 Dual Runtime Support on Samsung Galaxy A36 5G (GAP-03 & GAP-04)
- **Problem:** ONNX Runtime Mobile provides broad compatibility, but Google LiteRT / TFLite with Qualcomm NNAPI or GPU delegate offers lower invocation overhead and hardware INT8 tensor execution on the Snapdragon 6 Gen 3 Hexagon processor.
- **Solution:**
  1. Add LiteRT / TFLite support to the Android application alongside ONNX Runtime.
  2. Provide quantized `.tflite` model files (FP16 and INT8) in `app/src/main/assets/`.
  3. Include an auto-fallback mechanism: Attempt NPU/GPU hardware delegate first; fall back gracefully to multi-threaded CPU execution if delegates are unavailable.

### 3.3 Gamepad Telemetry & Diagnostic HUD (GAP-05 & GAP-06)
- **Problem:** In the field, operators need instant feedback when pairing the Cosmic Byte Ares Pro gamepad (e.g., verifying if the controller is in Android HID mode, D-Input, or X-Input).
- **Solution:**
  1. Expand the Android Cockpit HUD overlay with a gamepad diagnostics modal displaying real-time stick deflection vectors, trigger positions (0–100%), and active speed profile (`ECO` vs `SPORT`).
  2. Implement a two-way UDP heartbeat: ESP8266 echoes received packet sequence numbers, allowing the Android HUD to compute and display true round-trip network latency in milliseconds.

### 3.4 Architecture & Documentation Compliance (GAP-07 & GAP-08)
- **Problem:** Files are currently distributed across `01_` to `07_` numbered folders. The target layout specified in Section 13 requires clean top-level directories (`android-app/`, `esp8266-firmware/`, `ai-training/`, `models/`, `dataset/`, `tests/`, `docs/`, `scripts/`).
- **Solution:**
  1. Safely migrate files into the target directories with full path compatibility updates.
  2. Author all 20 required markdown guides in `docs/` and root.
