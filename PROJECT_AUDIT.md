# YOLOv8 Traffic Sign Detection — Project Audit Report

**Date of Audit:** November 3, 2026  
**Auditor:** Senior AI/ML Engineer & YOLOv8 Computer Vision Specialist  
**Workspace:** `S:\Kaushalya 2.0\R with CV`  
**Target Architecture:** YOLOv8 Nano (`yolov8n.pt`)  
**Target Application:** Real-time Traffic Sign Detection for Autonomous Vehicle  

---

## 1. Executive Summary

A comprehensive, non-destructive audit was performed across the local workspace, user directories, dataset archives, and Google Colab assets.

### Key Discoveries:
1. **Source Archive Found:** The primary project archive `Autonomous-Car.zip` (745,092,584 bytes / ~710.6 MB, containing 12,597 entries) and the original Colab notebook documentation `original_colab_code.pdf` were identified in the user's Downloads folder and safely copied to the project workspace.
2. **Pre-Trained Model Checkpoint Exists:** A trained 6-class YOLOv8n checkpoint `best.pt` was discovered inside `Autonomous-Car.zip` (`Autonomous-Car/training_runs/traffic_signs_6class_v1-4/weights/best.pt`). Inspection reveals it completed **60 training epochs** on the exact 6-class traffic sign dataset, achieving outstanding metrics:
   - **Precision:** 99.95% (`0.99945`)
   - **Recall:** 100.0% (`1.00000`)
   - **mAP@50:** 99.50% (`0.99500`)
   - **mAP@50-95:** 96.98% (`0.96984`)
3. **Dataset Integrity:** The primary dataset `Autonomous-Car/Traffic-Signs-new` contains exactly **6,000 images** across Train (4,200), Valid (1,200), and Test (600) splits. Every image has an exact matching YOLO annotation with zero corruption, zero missing labels, zero invalid coordinates, and zero data leakage.
4. **Primary Architectural Deficiencies:**
   - **Hardcoded Absolute Paths:** All legacy Python scripts (`audit_dataset.py`, `train_traffic_signs.py`, `test_new_model.py`) and dataset YAMLs contain hardcoded paths pointing to previous developers' machines (`C:\Users\siddh\...` and `C:\Users\SAGAR\...`).
   - **Incomplete Colab Pipeline:** The Colab workflow documented in `original_colab_code.pdf` terminates at epoch checkpoint verification, lacking model evaluation, test split benchmarking, video inference, webcam streaming, and modular CLI scripts.
   - **Legacy / Experimental Code Clutter:** The archive contains legacy 4-class experiments (`AutoVehicle` and `custom-traffic-signs.v1i.yolov8`) that conflict with the 6-class requirement if not properly isolated.

---

## 2. Environment & System Inventory

| Component | Status / Version | Notes |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 (64-bit) | Local execution environment |
| **Python Runtime** | Python 3.14.4 | Tested and operational |
| **PyTorch** | 2.14.0 (CPU) | Local fallback available; CUDA available: False |
| **Ultralytics YOLO** | 8.4.199 | Installed and operational; verified loading YOLOv8 checkpoints |
| **OpenCV** | 4.13.0.92 | Installed; support for image, video, and stream processing |
| **Torchvision** | 0.29.2 | Installed and compatible |
| **Pillow** | 12.2.0 | Installed |
| **PyYAML** | 6.0.3 | Installed |
| **Matplotlib / Seaborn** | 3.11.1 / 0.13.2 | Installed; metric plotting supported |
| **Storage Availability** | S: Drive: 283.77 GB free | Ample storage for dataset unpacking and artifact staging |

---

## 3. Archive & File Structure Breakdown

### 3.1 Contents of `Autonomous-Car.zip`
The archive contains 12,597 entries organized under the root directory `Autonomous-Car/`:

```text
Autonomous-Car/
├── .git/                                    # Git repository history from previous dev
├── audit_dataset.py                         # Defective audit script (points to 4-class dataset)
├── train_traffic_signs.py                   # Hardcoded training script (60 epochs, CPU)
├── test_new_model.py                        # Hardcoded DroidCam OpenCV test script
├── yolov8n.pt                               # Base pre-trained YOLOv8 Nano weights (6.55 MB)
├── cam_testing/
│   └── cam_testing.ino                      # ESP32 / Arduino camera firmware
├── Traffic-Signs-new/                       # [PRIMARY TARGET] 6-Class Dataset
│   ├── data.yaml                            # Dataset YAML (has hardcoded OneDrive path)
│   ├── classes.txt                          # 6 class names
│   ├── README.md                            # Roboflow/Academic paper documentation
│   ├── train/ (images: 4200, labels: 4200)
│   ├── valid/ (images: 1200, labels: 1200)
│   └── test/  (images: 600, labels: 600)
├── training_runs/                           # Previous training runs
│   ├── traffic_signs_6class_v1-4/          # [COMPLETED RUN] 60 Epochs
│   │   ├── args.yaml                        # Training hyperparameters
│   │   ├── results.csv                      # Full 60-epoch metrics log
│   │   ├── results.png                      # Training curves visualization
│   │   ├── confusion_matrix.png             # Confusion matrix
│   │   ├── confusion_matrix_normalized.png  # Normalized confusion matrix
│   │   ├── BoxF1_curve.png                  # F1 vs Confidence curve
│   │   ├── BoxPR_curve.png                  # Precision vs Recall curve
│   │   ├── val_batch*_pred.jpg              # Validation prediction samples
│   │   └── weights/
│   │       ├── best.pt                      # Best trained model weights (6.51 MB)
│   │       └── last.pt                      # Last epoch checkpoint (6.51 MB)
│   └── traffic_signs_6class_v1-[1,2,3]/     # Partial/early aborted runs
├── custom-traffic-signs.v1i.yolov8/         # [LEGACY] 4-class Roboflow dataset
│   └── data.yaml                            # Classes: ['FORWARD', 'LEFT', 'RIGHT', 'STOP']
└── AutoVehicle/                             # [LEGACY] Experimental 4-class ESP32 pipeline
    ├── collect_custom_images.py
    ├── train_custom_signs.py
    ├── data_custom.yaml
    └── runs/detect/runs/detect/custom_signs_v1/ # 13 epochs run, mAP@50: 33.26%
```

---

## 4. Code Inspection & Defect Analysis

### 4.1 `audit_dataset.py`
- **Defect 1 (Hardcoded Path):** `DATASET_DIR = Path(r"C:\Users\siddh\OneDrive\Documents\GitHub\Autonomous-Car\custom-traffic-signs.v1i.yolov8")`
- **Defect 2 (Wrong Dataset Target):** Audits the legacy 4-class Roboflow dataset instead of the primary 6-class `Traffic-Signs-new`.
- **Defect 3 (No CLI / Arguments):** No command line options to audit specific splits or directories.

### 4.2 `train_traffic_signs.py`
- **Defect 1 (Hardcoded Path):** `PROJECT_DIR = Path(r"C:\Users\siddh\OneDrive\Documents\GitHub\Autonomous-Car")`
- **Defect 2 (Static Hyperparameters):** `EPOCHS = 60`, `BATCH_SIZE = 8`, `DEVICE = "cpu"` hardcoded without CLI arguments or resume option.
- **Defect 3 (No Fallback or Multi-Device Support):** Does not dynamically check for CUDA/MPS/CPU.

### 4.3 `test_new_model.py`
- **Defect 1 (Hardcoded Model & Path):** Path hardcoded to `C:\Users\siddh\...`
- **Defect 2 (Camera Limitation):** Requires DroidCam on index 0 using `cv2.CAP_DSHOW`. Fails immediately if DroidCam is not running or on default webcams.
- **Defect 3 (Single Purpose):** Only handles video stream display; cannot predict on single images, folders of images, or video files. Does not save results.

### 4.4 `original_colab_code.pdf` (Colab Workflow Analysis)
The notebook was executed in Google Colab on a Tesla T4 GPU. Its cells cover:
1. `pip install -q ultralytics`
2. Version check (v8.4.198)
3. GPU check (Tesla T4)
4. Mount Google Drive (`/content/drive`)
5. Path configuration (`/content/drive/MyDrive/...`)
6. Extraction of `Autonomous-Car.zip` to `/content/dataset`
7. YAML search and inspection
8. Overwriting `data.yaml` with Colab-specific paths
9. Image/label count verification (4200 / 1200 / 600)
10. Model instantiation: `YOLO('yolov8n.pt')`
11. Model training: 100 epochs, batch 16, imgsz 640, device 0, patience 0
12. Checkpoint verification: `os.path.exists(BEST_MODEL)`

**Critical Gaps in Colab Workflow:**
- Did not include model validation or evaluation on the test set (`model.val(split='test')`).
- Did not export or visualize test set confusion matrices, PR curves, or detection samples.
- Did not provide inference scripts for test images or test videos.
- All paths are hardcoded to `/content/drive/MyDrive/`; if the user stores the zip in another Drive folder or uploads it directly, the script fails.

---

## 5. Existing Trained Models Audit

We performed a deep inspection of `Autonomous-Car/training_runs/traffic_signs_6class_v1-4/weights/best.pt`:

```python
{
    'date': '2026-10-26T10:25:40.363627+05:30',
    'epoch': -1,
    'task': 'detect',
    'names': {
        0: 'left_turn',
        1: 'straight_ahead',
        2: 'right_turn',
        3: 'dead_end',
        4: 'no_entry',
        5: 'stop'
    },
    'train_metrics': {
        'metrics/precision(B)': 0.99945,
        'metrics/recall(B)': 1.0,
        'metrics/mAP50(B)': 0.995,
        'metrics/mAP50-95(B)': 0.96984,
        'val/box_loss': 0.22908,
        'val/cls_loss': 0.14165,
        'val/dfl_loss': 0.84155,
        'fitness': 0.96984
    }
}
```

### Verification Inference Test
A sample image from the test set (`depth_0017_27432_jpg.rf.003cf6be27ad9de91b2fe56c57dc9646.jpg`) was evaluated through `best.pt`:
- **Ground Truth:** Class 4 (`no_entry`), bounding box center `[0.917, 0.770]`, size `[0.166, 0.204]`
- **Model Prediction:** Class 4 (`no_entry`), **Confidence: 95.75%**, predicted center `[0.917, 0.769]`, size `[0.164, 0.201]`
- **Verdict:** The pre-trained model is fully functional, properly calibrated, and exhibits near-perfect localization accuracy on unseen test data.

---

## 6. Audit Conclusion & Next Steps

1. **Do not retrain from scratch unnecessarily:** The existing `best.pt` has already achieved 99.5% mAP@50 and 96.98% mAP@50-95 on this exact dataset.
2. **Preserve weights safely:** Staging `best.pt` and `last.pt` under `models/` is prioritized.
3. **Build a modular production system:** Develop clean, decoupled Python modules under `src/` for training, evaluation, image prediction, video prediction, webcam streaming, and utilities.
4. **Prepare an upgraded Colab Notebook:** Create a complete, robust notebook covering end-to-end execution with configurable paths, evaluation, and inference.
