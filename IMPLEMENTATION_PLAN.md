# YOLOv8 Traffic Sign Detection — Implementation Plan

**Date:** November 3, 2026  
**Author:** Senior AI/ML Engineer & YOLOv8 Computer Vision Specialist  
**Target Environment:** Local Windows Machine (CPU fallback/Inference) & Google Colab (GPU Training/Validation)  
**Model Architecture:** YOLOv8 Nano (`yolov8n.pt`)  
**Classes:** 6 Classes (`left_turn`, `straight_ahead`, `right_turn`, `dead_end`, `no_entry`, `stop`)  

---

## 1. Project Goals & Architecture Overview

The goal is to transition an ad-hoc, hardcoded YOLOv8 training script and a raw dataset archive into an organized, production-grade Traffic Sign Detection system for autonomous vehicles.

```text
YOLOv8-Traffic-Sign-Detection/
│
├── dataset/                         # Extracted 6-class dataset (Traffic-Signs-new)
│   ├── train/ (images, labels)
│   ├── valid/ (images, labels)
│   └── test/  (images, labels)
│
├── models/                          # Model checkpoints
│   ├── best.pt                      # 60-epoch trained model (99.5% mAP50)
│   ├── last.pt                      # Checkpoint from last epoch
│   └── yolov8n.pt                   # Base pre-trained YOLOv8 Nano model
│
├── configs/
│   └── data.yaml                    # Portable dataset YAML configuration
│
├── src/                             # Modular Python engine
│   ├── __init__.py
│   ├── utils.py                     # Device auto-detect, visualization, box drawing, metrics
│   ├── train.py                     # Configurable training pipeline (CLI, resume, GPU/CPU)
│   ├── evaluate.py                  # Evaluation & test split benchmark (mAP, confusion matrix)
│   ├── predict_image.py             # Single / batch image detection with visualization & JSON
│   ├── predict_video.py             # Video stream detection, FPS tracking, annotated MP4 output
│   └── webcam.py                    # Real-time webcam / RTSP / USB / DroidCam stream detection
│
├── outputs/                         # Default inference & evaluation output directory
│   ├── predictions/                 # Annotated images & prediction logs
│   ├── videos/                      # Annotated video outputs
│   └── evaluation/                  # Confusion matrix, PR curves, validation plots
│
├── notebooks/
│   └── YOLOv8_Traffic_Sign_Detection.ipynb  # Self-contained Google Colab notebook
│
├── requirements.txt                 # Clean pinned dependencies
├── README.md                        # Documentation & quickstart guide
├── PROJECT_AUDIT.md                 # System & environment audit report
├── DATASET_AUDIT.md                 # Deep dataset & annotation audit report
└── IMPLEMENTATION_PLAN.md           # This execution roadmap
```

---

## 2. Phase-by-Phase Execution Plan

### Phase 1 — Project Inspection (COMPLETED)
- Scanned directory, located `Autonomous-Car.zip` and `original_colab_code.pdf`.
- Inspected Python 3.14.4, PyTorch 2.14.0, Ultralytics 8.4.199 environment.
- Documented in `PROJECT_AUDIT.md`.

### Phase 2 — Dataset & Model Audit (COMPLETED)
- Verified all 6,000 images and 6,000 labels in `Traffic-Signs-new`.
- Audited label formats, coordinate bounds, class distribution, and zero data leakage.
- Inspected existing checkpoint `best.pt` (verified 60 epochs, 99.5% mAP@50, 100% recall).
- Tested inference on unseen test sample.
- Documented in `DATASET_AUDIT.md`.

### Phase 3 — Audit Documentation (COMPLETED)
- Created `PROJECT_AUDIT.md` and `DATASET_AUDIT.md`.
- Staged `IMPLEMENTATION_PLAN.md`.

### Phase 4 — Implementation Alignment & Safety Guarantees (CURRENT)
- Do not overwrite existing models or dataset files.
- Maintain original zip archive as the master backup.
- Unpack only required files without cluttering.

### Phase 5 — Environment Setup & Asset Extraction
1. **Model Weights Preservation:**
   - Extract `Autonomous-Car/training_runs/traffic_signs_6class_v1-4/weights/best.pt` to `models/best.pt`.
   - Extract `Autonomous-Car/training_runs/traffic_signs_6class_v1-4/weights/last.pt` to `models/last.pt`.
   - Extract base model `Autonomous-Car/yolov8n.pt` to `models/yolov8n.pt`.
   - Extract training plots (`results.csv`, `results.png`, `confusion_matrix.png`, etc.) to `outputs/evaluation/` to preserve historical evidence.
2. **Dataset Deployment:**
   - Extract `Traffic-Signs-new` into `dataset/` (`train`, `valid`, `test`).
   - Create portable `configs/data.yaml` referencing `dataset/` using relative and dynamically resolvable paths.

### Phase 6 — Core Software Engineering (`src/` Modules)
1. **`src/utils.py`:**
   - Device auto-selection logic (`cuda:0` if available, else `cpu`).
   - Class ID-to-name mapping and color palette generation for traffic signs.
   - Bounding box rendering utilities with confidence percentage badges.
   - Output directory management and JSON serialization helpers.
2. **`src/train.py`:**
   - Argument parser (`--data`, `--epochs`, `--batch`, `--imgsz`, `--device`, `--workers`, `--patience`, `--optimizer`, `--resume`, `--project`, `--name`).
   - Validation that dataset YAML exists and points to valid directories.
   - Resume capability from `--resume <checkpoint>`.
   - Fallback logic for device selection.
   - Automatic logging of final training metrics.
3. **`src/evaluate.py`:**
   - Argument parser (`--model`, `--data`, `--split`, `--imgsz`, `--batch`, `--device`, `--project`, `--name`).
   - Runs `model.val()` on specified split (`test` or `val`).
   - Extracts and displays overall and per-class metrics:
     - Precision
     - Recall
     - mAP@50
     - mAP@50-95
   - Saves confusion matrix, precision-recall curves, and plots into `outputs/evaluation/`.
4. **`src/predict_image.py`:**
   - Argument parser (`--model`, `--source`, `--conf`, `--iou`, `--imgsz`, `--device`, `--save-dir`, `--no-save`).
   - Handles single image file or directory of images.
   - Draws labeled bounding boxes, displays detections, and exports JSON summary with file name, class, confidence, and box coordinates.
5. **`src/predict_video.py`:**
   - Argument parser (`--model`, `--source`, `--output`, `--conf`, `--iou`, `--imgsz`, `--device`, `--show`).
   - Processes input video frame-by-frame using OpenCV.
   - Computes rolling inference FPS and displays on-screen overlay.
   - Writes encoded output MP4 file with annotated bounding boxes.
6. **`src/webcam.py`:**
   - Argument parser (`--model`, `--camera-index`, `--stream-url`, `--conf`, `--iou`, `--width`, `--height`, `--device`).
   - Flexible video source: accepts camera index (0, 1, 2) or IP camera stream URL (RTSP/HTTP/DroidCam).
   - Real-time display with FPS counter, class labels, and confidence.
   - Interactive key commands: `q` to quit, `s` to save snapshot, `c` to toggle confidence threshold.
   - Graceful camera release and window closure on keyboard interrupt or error.

### Phase 7 — Verification & Testing
1. Test Python syntax and imports across all modules.
2. Test CLI `--help` flags for all 5 scripts.
3. Execute real inference with `models/best.pt` on test images via `predict_image.py`.
4. Execute benchmark evaluation on test split via `evaluate.py`.
5. Verify output artifact generation in `outputs/predictions/` and `outputs/evaluation/`.

### Phase 8 — Google Colab Notebook (`notebooks/YOLOv8_Traffic_Sign_Detection.ipynb`)
Create a complete, beautifully structured, executable Colab notebook:
- Section 1: GPU verification & environment setup.
- Section 2: Google Drive mounting & dataset setup (supports ZIP extraction or direct upload).
- Section 3: Dynamic YAML path generation (prevents path mismatches).
- Section 4: Dataset count and structure verification.
- Section 5: Model training with YOLOv8 Nano (supports configurable epochs and checkpoint saving to Google Drive).
- Section 6: Model validation & test evaluation (mAP@50, mAP@50-95, per-class breakdown).
- Section 7: Visualization of training curves, confusion matrix, and PR curves.
- Section 8: Image inference and side-by-side visualization.
- Section 9: Video inference on sample footage.
- Section 10: Model export (ONNX, TorchScript) for embedded autonomous car deployment.

### Phase 9 — Final Documentation & Deliverables
- Write comprehensive `README.md` with problem statement, class descriptions, installation, local usage, Colab guide, and autonomous vehicle integration notes.
- Write clean `requirements.txt`.
- Present final summary to the user.
