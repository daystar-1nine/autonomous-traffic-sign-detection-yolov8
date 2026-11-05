# 07 - Technical Model Benchmark Report

This report presents empirical performance metrics for the YOLOv8 models evaluated on the **600-image unseen test set** of the autonomous traffic signs benchmark.

---

## 🏆 Overall Test Set Benchmark Scores

| Metric | YOLOv8n (Nano - Mobile Primary) | YOLOv8s (Small - High Capacity) |
| :--- | :---: | :---: |
| **Precision (P)** | **100.00%** (`1.0000`) | **100.00%** (`1.0000`) |
| **Recall (R)** | **100.00%** (`1.0000`) | **100.00%** (`1.0000`) |
| **mAP @ 0.50** | **99.50%** (`0.9950`) | **99.50%** (`0.9950`) |
| **mAP @ 0.50:0.95** | **97.25%** (`0.9725`) | **97.54%** (`0.9754`) |
| **Parameters** | **3.13 Million** | 11.14 Million |
| **FLOPs @ 640×640** | **8.6 GFLOPs** | 28.5 GFLOPs |
| **PyTorch Weight Size** | **6.2 MB** | 22.5 MB |
| **Exported ONNX Size** | **12.2 MB** | 44.1 MB |
| **Quantized FP16 TFLite** | **~6.1 MB** | ~22.0 MB |
| **GPU Inference Latency** | **4.2 ms** (RTX 5060) | 4.8 ms (RTX 5060) |
| **Mobile CPU Latency** | **~24 ms** (~41 FPS) | ~85 ms (~12 FPS) |

---

## 📊 Per-Class Test Breakdown (YOLOv8n Mobile Primary)

Evaluated on 100 test samples per class (uniform test split):

| Class ID | Class Name | Precision | Recall | mAP@50 | mAP@50-95 |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **0** | `left_turn` | 100.0% | 100.0% | 99.50% | 99.50% |
| **1** | `straight_ahead` | 100.0% | 100.0% | 99.50% | 94.06% |
| **2** | `right_turn` | 100.0% | 100.0% | 99.50% | 94.48% |
| **3** | `dead_end` | 100.0% | 100.0% | 99.50% | 98.05% |
| **4** | `no_entry` | 100.0% | 100.0% | 99.50% | 99.50% |
| **5** | `stop` | 100.0% | 100.0% | 99.50% | 97.94% |

---

## 🔬 Confusion Matrix Analysis

- **False Positive Rate (FPR):** **0.00%** across all classes at confidence threshold $\ge 0.60$.
- **False Negative Rate (FNR):** **0.00%** on genuine sign targets.
- **Inter-Class Confusion:** 0 instances of cross-class misclassification (e.g. left turn was never misidentified as right turn or straight ahead).
