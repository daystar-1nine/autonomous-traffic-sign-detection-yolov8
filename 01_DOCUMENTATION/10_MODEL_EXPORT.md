# 10 - Mobile AI Model Export & Optimization Guide

This document explains how to export trained PyTorch checkpoints (`.pt`) to optimized mobile inference formats (**ONNX**, **TFLite**, and **NCNN**) for deployment on Android.

---

## 📱 Mobile Runtime Comparison

| Format | Runtime | Strengths | Ideal Hardware Target |
| :--- | :--- | :--- | :--- |
| **TFLite (FP16 / FP32)** | TensorFlow Lite / Google Play Services | Direct Android Java/Kotlin API, GPU delegate support, zero NDK compilation needed. | **Android Phones (Redmi Note/Series)** |
| **ONNX** | ONNX Runtime Mobile | Standard cross-platform format, direct model graph inspection in [Netron](https://netron.app). | Desktop, Embedded Linux, Android |
| **NCNN** | Tencent NCNN (C++ NDK) | Ultra-low memory, custom ARM NEON assembly kernels. | Older ARMv7 / low-end Android CPUs |

---

## 🛠️ Export Commands

### 1. Export to ONNX (Graph Verified)
```powershell
python "02_AI_MODEL/scripts/export_model.py" --model "02_AI_MODEL/weights/best_yolov8n.pt" --format onnx --imgsz 640
```
- Output file: `02_AI_MODEL/exports/best_yolov8n.onnx` (12.2 MB).

### 2. Export to TFLite (TensorFlow Lite)
```powershell
python "02_AI_MODEL/scripts/export_model.py" --model "02_AI_MODEL/weights/best_yolov8n.pt" --format tflite --imgsz 640
```

### 3. Export to FP16 Half-Precision TFLite (Recommended for Mobile GPU)
Reduces model size by 50% without measurable accuracy drop:
```powershell
python "02_AI_MODEL/scripts/export_model.py" --model "02_AI_MODEL/weights/best_yolov8n.pt" --format tflite --half --imgsz 640
```

---

## 📂 Deploying to the Android Project

Copy the exported model into the Android app's `assets/` folder:

```powershell
Copy-Item "02_AI_MODEL/exports/best_yolov8n_float32.tflite" -Destination "03_ANDROID_APP/app/src/main/assets/yolov8n.tflite"
```

---

## 🔬 Tensor Graph Specifications

- **Input Tensor (`images`):**
  - Dimensions: `[1, 3, 640, 640]`
  - Format: RGB normalized $\in [0.0, 1.0]$ in BCHW layout
- **Output Tensor (`output0`):**
  - Dimensions: `[1, 10, 8400]`
  - 10 rows per anchor = $[x_{\text{center}}, y_{\text{center}}, \text{width}, \text{height}, p_0, p_1, p_2, p_3, p_4, p_5]$
  - 8,400 anchors = candidate multi-scale grid cells ($80\times 80 + 40\times 40 + 20\times 20$).

---

👉 **Next Step:** Proceed to [`11_ANDROID_SETUP.md`](11_ANDROID_SETUP.md) to prepare Android Studio.
