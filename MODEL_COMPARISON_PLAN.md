# MODEL COMPARISON & SELECTION PLAN
**Autonomous AI Traffic Sign Detection Car — Beyond YOLO**
**Hardware Profile:** Samsung Galaxy A36 5G (Qualcomm Snapdragon 6 Gen 3, 8GB RAM, Adreno 710 GPU, Hexagon NPU)
**Plan Date:** 2026-11-06 | **Lead:** Senior AI/ML & Embedded Systems Architect

---

## 1. Objective & Scope

While the existing YOLOv8n implementation achieves outstanding accuracy (0.995 mAP@0.5) on desktop and initial tests, deploying an autonomous vehicle on a mobile device (Samsung Galaxy A36 5G) demands evaluating the broader landscape of edge object detectors.

This plan defines an empirical evaluation protocol comparing **YOLOv8n** against leading alternative edge architectures:
1. **EfficientDet-Lite0** (Google AutoML)
2. **SSD MobileNetV2** (Google MobileNet)
3. **NanoDet-Plus** (Anchor-free edge detector)
4. **PP-PicoDet-S/M** (Baidu PaddlePaddle)
5. **RT-DETR-Tiny/Mobile** (Real-Time Detection Transformer)

---

## 2. Target Device Architectural Constraints (Samsung Galaxy A36 5G)

The AI model runs directly on the smartphone mounted to the robot chassis under real driving conditions:
- **Processor:** Qualcomm Snapdragon 6 Gen 3 (4nm TSMC, 4× Cortex-A78 @ 2.40 GHz + 4× Cortex-A55 @ 1.80 GHz).
- **GPU Accelerator:** Qualcomm Adreno 710 with support for Vulkan 1.3, OpenGL ES 3.2, and OpenCL 2.0 FP16.
- **NPU / DSP:** Qualcomm Hexagon NPU with Vector eXtensions (HVX), optimized for 8-bit integer tensor math (`INT8`).
- **Memory Bandwidth:** LPDDR4X @ 2133 MHz (shared unified memory with Android OS and CameraX buffer).
- **Battery & Thermal Limits:** The phone must run continuous vision inference at 30 FPS alongside CameraX 1080p preview, Bluetooth gamepad polling, and UDP telemetry transmission without exceeding a 4.0W thermal budget or causing thermal throttling over 30 minutes of continuous operation.

---

## 3. Candidate Model Architecture Profiles

### 3.1 YOLOv8n (Baseline)
- **Developer:** Ultralytics (2023)
- **Parameters:** 3.13 Million | **FLOPs:** 8.7 GFLOPs @ 640×640
- **Architecture:** Anchor-free decoupled head, C2f (Cross-Stage Partial with 2 convolutions) feature extractor, SPPF pooling, Task-Aligned Assigner.
- **Runtime:** ONNX Runtime Mobile, TFLite (FP16/INT8), PyTorch Mobile.
- **Pros:** State-of-the-art mAP, pre-trained weights readily available, proven 99.5% mAP50 on our 6-class dataset.
- **Cons:** Standard 640×640 input resolution incurs higher memory bandwidth on mobile CPU.

### 3.2 EfficientDet-Lite0
- **Developer:** Google Research / AutoML (2020)
- **Parameters:** 4.40 Million | **FLOPs:** 2.5 GFLOPs @ 320×320
- **Architecture:** EfficientNet-Lite0 backbone (no squeeze-and-excitation for mobile efficiency), BiFPN (Weighted Bi-directional Feature Pyramid Network), compound scaling.
- **Runtime:** Native Google LiteRT / TensorFlow Lite (TFLite).
- **Pros:** Specifically architected for integer quantization (INT8) with zero post-quantization accuracy degradation; minimal memory footprint; native TFLite Task Library support on Android.
- **Cons:** Slightly slower inference on mobile GPU compared to anchor-free detectors due to multi-scale anchor generation.

### 3.3 SSD MobileNetV2
- **Developer:** Google (2018–2019)
- **Parameters:** 3.50 Million | **FLOPs:** 1.2 GFLOPs @ 300×300
- **Architecture:** MobileNetV2 backbone (Inverted Residuals with Linear Bottlenecks, Depthwise Separable Convolutions), Multi-Box Single Shot Detector head.
- **Runtime:** Native Google LiteRT / TFLite, Android NNAPI.
- **Pros:** Universally supported across Android versions, ultra-low CPU consumption (~8-12 ms on Cortex-A78), minimal battery draw.
- **Cons:** Bounding box regression accuracy and small-object detection typically lower than modern anchor-free architectures (mAP50 usually ~85-90%).

### 3.4 NanoDet-Plus
- **Developer:** RangiLyu (2021–2022)
- **Parameters:** 1.17 Million | **FLOPs:** 0.9 GFLOPs @ 320×320
- **Architecture:** ShuffleNetV2 1.0x backbone, Ghost-PAN feature fusion, anchor-free decoupled head, Generalized Focal Loss (GFL).
- **Runtime:** NCNN, ONNX Runtime Mobile, MNN.
- **Pros:** Ultra-compact (<3 MB model file), sub-6 ms inference on mobile CPU, anchor-free design ideal for traffic sign aspect ratios.
- **Cons:** Requires custom NCNN or ONNX post-processing pipeline in Android; no native TFLite Task Library wrapper.

### 3.5 PP-PicoDet-S
- **Developer:** Baidu PaddlePaddle (2021)
- **Parameters:** 0.99 Million | **FLOPs:** 0.7 GFLOPs @ 320×320
- **Architecture:** Enhanced ShuffleNet (ESNet) backbone, CSP-PAN, SimOTA dynamic label assignment.
- **Runtime:** Paddle-Lite, ONNX Runtime, TFLite (via Paddle2ONNX conversion).
- **Pros:** Highest accuracy-to-compute ratio among sub-1M parameter models; fast inference on ARM NEON.
- **Cons:** Multi-step export pipeline (PaddlePaddle -> ONNX -> TFLite) introduces risk of unsupported operator conversions.

### 3.6 RT-DETR-Tiny (Real-Time Detection Transformer)
- **Developer:** Baidu (2023)
- **Parameters:** ~20.0 Million | **FLOPs:** ~60 GFLOPs @ 640×640
- **Architecture:** CNN backbone with Efficient Hybrid Encoder and Transformer decoder with Hungarian matching.
- **Pros:** Superior context modeling, eliminates NMS post-processing.
- **Cons:** **Infeasible for this application.** 20M+ parameters and 60 GFLOPs will saturate mobile thermals on Snapdragon 6 Gen 3 and drop below 10 FPS on battery.

---

## 4. Empirical Evaluation Protocol

The evaluation protocol benchmarks each candidate architecture under identical test conditions:

### 4.1 Benchmark Metrics Matrix
1. **Accuracy Metrics (on 600-image Test Split):**
   - $\text{mAP@0.5}$ (Primary detection threshold)
   - $\text{mAP@0.5:0.95}$ (Localization precision)
   - Per-class Recall for safety-critical signs (`stop`, `no_entry`)
2. **Computational Metrics:**
   - Parameter Count ($M$)
   - Model File Size: FP32, FP16, and INT8 ($MB$)
   - Theoretical Multiply-Accumulates ($GFLOPs$)
3. **Runtime Metrics on Snapdragon 6 Gen 3:**
   - CPU Inference Latency (4 threads, milliseconds)
   - GPU Inference Latency (Adreno 710 Vulkan/OpenCL delegate, milliseconds)
   - NPU Inference Latency (Qualcomm Hexagon NNAPI INT8, milliseconds)
   - End-to-End Pipeline Latency (CameraX frame buffer -> Inference -> Post-processing -> UDP transmit)
   - Sustained FPS over 15 minutes continuous execution
   - Peak RAM Consumption ($MB$)

### 4.2 Scoring & Decision Weighting Matrix

| Evaluation Dimension | Weight (%) | Target Benchmark Criterion |
| :--- | :---: | :--- |
| **Safety & Accuracy ($\text{mAP@0.5}$)** | **35%** | $\ge 95.0\%$ overall; $\ge 98.0\%$ on `stop` and `no_entry` |
| **Inference Latency on Snapdragon 6 Gen 3** | **25%** | $\le 25\text{ ms}$ ($\ge 40\text{ FPS}$ throughput capability) |
| **Hardware Acceleration & Quantization** | **15%** | Seamless INT8 / FP16 conversion without accuracy collapse ($<1.5\%\Delta$) |
| **Android Integration & Runtime Stability** | **15%** | Native Android execution (LiteRT/TFLite or ONNX Runtime Mobile) |
| **Thermal & Power Efficiency** | **10%** | Sustained $<3.5\text{W}$ consumption; zero thermal throttling at 30 FPS |

---

## 5. Deployment Recommendation Framework

Based on architectural profiling and preliminary benchmark data:
- **Primary Production Choice:** **YOLOv8n (FP16 / INT8 quantized)** or **EfficientDet-Lite0 (INT8)**.
  - If **YOLOv8n** achieves sub-18 ms on Snapdragon 6 Gen 3 GPU/NPU while retaining 99.5% mAP, it remains the superior balance of localization precision and real-world robustness.
  - If CPU thermals or battery conservation are prioritized above all else, **EfficientDet-Lite0 (INT8)** or **NanoDet-Plus** provides an ultra-lightweight alternative.
- **Model Delivery:** The project will provide both:
  1. Selected production model exported in `.tflite` (with metadata, labels, and quantized tensors) and `.onnx` formats.
  2. The standalone dataset conversion script `yolo_to_coco.py` to allow training any alternative detector seamlessly.
