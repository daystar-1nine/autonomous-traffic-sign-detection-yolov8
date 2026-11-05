# 09 - Neural Network Training & Validation Guide

This document details the exact procedures for training, fine-tuning, and evaluating the **YOLOv8** traffic sign detection models.

---

## 🎯 Dataset Configuration (`02_AI_MODEL/dataset/data.yaml`)

```yaml
path: S:/Kaushalya 2.0/R with CV/dataset
train: train/images
val: valid/images
test: test/images

nc: 6
names:
  0: left_turn
  1: straight_ahead
  2: right_turn
  3: dead_end
  4: no_entry
  5: stop
```

---

## 🚀 Training Commands

### 1. Train Primary Mobile Model (YOLOv8 Nano)
Fastest training, lightweight 3.13M parameters, optimal for Android deployment:

```powershell
python "02_AI_MODEL/scripts/train.py" --model yolov8n.pt --epochs 60 --batch 16 --imgsz 640 --name traffic_signs_yolov8n
```

### 2. Train High-Capacity Baseline (YOLOv8 Small)
11.14M parameters for high-precision server/desktop benchmarking:

```powershell
python "02_AI_MODEL/scripts/train.py" --model yolov8s.pt --epochs 60 --batch 16 --imgsz 640 --name traffic_signs_yolov8s
```

### 3. Resume an Interrupted Training Run
```powershell
python "02_AI_MODEL/scripts/train.py" --resume "runs/train/traffic_signs_yolov8n/weights/last.pt"
```

---

## 📊 Evaluating Models on the Unseen Test Split

Run the automated evaluation benchmark on the 600 unseen test images:

```powershell
python "02_AI_MODEL/scripts/evaluate.py" --model "02_AI_MODEL/weights/best_yolov8n.pt" --split test
```

Expected benchmark output:
```text
============================================================
 EVALUATION BENCHMARK: best_yolov8n.pt on TEST SET
============================================================
 Precision (P)    : 1.0000 (100.00%)
 Recall (R)       : 1.0000 (100.00%)
 mAP @ 0.50       : 0.9950 (99.50%)
 mAP @ 0.50:0.95  : 0.9725 (97.25%)
------------------------------------------------------------
 Class 0 [left_turn      ]: P=1.000 | R=1.000 | mAP50=0.9950
 Class 1 [straight_ahead ]: P=1.000 | R=1.000 | mAP50=0.9950
 Class 2 [right_turn     ]: P=1.000 | R=1.000 | mAP50=0.9950
 Class 3 [dead_end       ]: P=1.000 | R=1.000 | mAP50=0.9950
 Class 4 [no_entry       ]: P=1.000 | R=1.000 | mAP50=0.9950
 Class 5 [stop           ]: P=1.000 | R=1.000 | mAP50=0.9950
```

---

👉 **Next Step:** Proceed to [`10_MODEL_EXPORT.md`](10_MODEL_EXPORT.md) to convert PyTorch weights to mobile runtimes.
