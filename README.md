# 🚗 YOLOv8 Traffic Sign Detection for Autonomous Vehicles

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-blue?logo=python)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/Ultralytics-YOLOv8s%20%2F%20YOLOv8n-00FFFF?logo=yolo)](https://github.com/ultralytics/ultralytics)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv)](https://opencv.org/)
[![mAP@50](https://img.shields.io/badge/mAP%4050-99.5%25-brightgreen)](outputs/evaluation/test_yolov8s_benchmarks)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade, real-time Computer Vision system for detecting and recognizing traffic signs from vehicle cameras. Engineered using **YOLOv8 Small (YOLOv8s)** with fallback to **YOLOv8 Nano (YOLOv8n)** for low-latency, edge-embedded deployment in autonomous cars, robotics platforms, and simulation test tracks.

---

## 📌 Problem Statement

Autonomous vehicles require instantaneous, high-precision detection of regulatory and directional traffic signs to ensure safe navigation, path planning, and obstacle avoidance. Missing a stop sign or misinterpreting a directional arrow poses severe safety risks. 

This project delivers a lightweight, highly accurate vision engine capable of running in real-time on edge compute devices (such as NVIDIA Jetson, Raspberry Pi, or onboard automotive microcomputers) while achieving **99.5% mAP@50** and **100% recall** on unseen test data.

---

## 🎯 Supported Traffic Sign Classes

The system detects and localizes **6 critical traffic sign classes**:

| Class ID | Sign Name | Meaning / Autonomous Driving Action | Icon / Visual |
| :---: | :--- | :--- | :---: |
| **0** | `left_turn` | Mandatory or permitted left turn ahead; trigger lane indicator | ⬅️ |
| **1** | `straight_ahead` | Forward path clear; proceed along lane trajectory | ⬆️ |
| **2** | `right_turn` | Mandatory or permitted right turn ahead; adjust steering angle | ➡️ |
| **3** | `dead_end` | No through road ahead; initiate turnaround or rerouting | 🛑 |
| **4** | `no_entry` | Restricted access; prohibit vehicle entry immediately | ⛔ |
| **5** | `stop` | Complete stop required at junction line; verify cross-traffic | 🛑 |

---

## 📊 Dataset Specifications & Provenance

The primary dataset (`Traffic-Signs-new`) is based on benchmarking research for embedded 1:10 scale autonomous vehicles captured using Intel RealSense D435i depth cameras in an urban simulation track.

- **Total Images:** 6,000 images (640 × 640 pixels, 3-channel JPEG)
- **Annotations:** CVAT-curated YOLO format (`<class_id> <x_center> <y_center> <width> <height>`)
- **Data Distribution:**
  - **Training Set (70%):** 4,200 images, 4,200 labels (exactly 700 images per class)
  - **Validation Set (20%):** 1,200 images, 1,200 labels (uniform class distribution)
  - **Testing Set (10%):** 600 images, 600 labels (unseen evaluation benchmark)
- **Quality Verification:**
  - **0** missing labels / images
  - **0** corrupted images
  - **0** duplicate images across splits (verified via MD5 hash analysis)
  - Exactly **1.0 bounding box per image** with normalized coordinates $\in [0, 1]$

---

## 🏆 Model Performance & Test Benchmarks

Evaluated on the **unseen 600-image test set** using the high-accuracy trained `models/best.pt` (YOLOv8s) checkpoint:

| Metric | Overall Benchmark Score |
| :--- | :---: |
| **Precision (P)** | **100.00%** (`1.0000`) |
| **Recall (R)** | **100.00%** (`1.0000`) |
| **mAP @ 0.50** | **99.50%** (`0.9950`) |
| **mAP @ 0.50:0.95** | **97.54%** (`0.9754`) |
| **Model Architecture** | YOLOv8 Small (`yolov8s.pt`) |
| **Model Parameters** | 11.14 Million |
| **Model GFLOPs** | 28.5 GFLOPs |
| **Inference Latency** | ~4.8 ms (NVIDIA RTX 5060) / ~85 ms (CPU) |

### Per-Class Test Split Breakdown
| Class ID | Class Name | Precision | Recall | mAP@50 | mAP@50-95 |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 0 | `left_turn` | 100.0% | 100.0% | 99.50% | 99.50% |
| 1 | `straight_ahead` | 100.0% | 100.0% | 99.50% | 94.51% |
| 2 | `right_turn` | 100.0% | 100.0% | 99.50% | 95.24% |
| 3 | `dead_end` | 100.0% | 100.0% | 99.50% | 98.23% |
| 4 | `no_entry` | 100.0% | 100.0% | 99.50% | 99.50% |
| 5 | `stop` | 100.0% | 100.0% | 99.50% | 98.24% |

*All evaluation metrics, confusion matrices, and precision-recall curves are stored in [`outputs/evaluation/test_yolov8s_benchmarks`](outputs/evaluation/test_yolov8s_benchmarks).*

---

## 📁 Project Folder Structure

```text
YOLOv8-Traffic-Sign-Detection/
│
├── dataset/                         # Extracted 6-class dataset
│   ├── train/ (images, labels)      # 4,200 training samples
│   ├── valid/ (images, labels)      # 1,200 validation samples
│   ├── test/  (images, labels)      # 600 benchmark testing samples
│   └── sample_signs/                # 1 showcase sample image per class
│
├── models/                          # Trained weights & checkpoints
│   ├── best.pt                      # 60-epoch trained model (99.5% mAP@50)
│   ├── last.pt                      # Last epoch checkpoint
│   └── yolov8n.pt                   # Pretrained base model
│
├── configs/
│   └── data.yaml                    # Portable dataset YAML configuration
│
├── src/                             # Modular Python engine
│   ├── __init__.py                  # Package init
│   ├── car_controller.py            # Master autonomous vehicle AI brain & telemetry
│   ├── utils.py                     # Device detection, HUD box rendering, helpers
│   ├── train.py                     # Configurable training pipeline (CLI, resume)
│   ├── evaluate.py                  # Evaluation & test split benchmark
│   ├── predict_image.py             # Single / batch image inference
│   ├── predict_video.py             # Video stream detection with telemetry
│   └── webcam.py                    # Live webcam, RTSP, DroidCam streaming
│
├── firmware/                        # Microcontroller IoT firmware
│   └── esp8266_car/                 # NodeMCU ESP8266 + TB6612FNG C++ Arduino sketch
│       └── esp8266_car.ino
│
├── HARDWARE_SETUP.md                # Circuit schematics, BOM, pinout & calibration guide
│
├── outputs/                         # Generated inference outputs
│   ├── predictions/                 # Labeled test images & JSON logs
│   ├── videos/                      # Annotated MP4 output videos
│   └── evaluation/                  # Confusion matrix, PR curves, logs
│       └── test_split_benchmarks/   # Full 600-image test benchmark plots
│
├── notebooks/
│   └── YOLOv8_Traffic_Sign_Detection.ipynb  # End-to-end Google Colab notebook
│
├── Autonomous-Car.zip               # Master source archive backup
├── original_colab_code.pdf          # Historical Colab workflow reference
├── requirements.txt                 # Pinned dependencies
├── PROJECT_AUDIT.md                 # Complete system audit report
├── DATASET_AUDIT.md                 # Deep dataset & annotation audit
├── IMPLEMENTATION_PLAN.md           # Execution roadmap & architecture
└── README.md                        # Documentation (this file)
```

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
