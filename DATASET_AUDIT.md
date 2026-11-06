# DATASET AUDIT REPORT
**Autonomous AI Traffic Sign Detection Car**
**Dataset Scope:** 6-Class Custom Road Traffic Sign Dataset
**Audit Date:** 2026-11-06 | **Auditor:** Senior AI/ML & Computer Vision Engineer

---

## 1. Executive Summary

A comprehensive automated audit of the dataset located at `dataset/` was conducted. The dataset comprises **6,000 high-resolution images** with ground-truth bounding box annotations divided into standard `train` (70%), `valid` (20%), and `test` (10%) splits.

The dataset exhibits exceptional class balance, zero corrupt images, 100% annotation pairing integrity, and strictly valid bounding box coordinates within normalized bounds `[0.0, 1.0]`.

---

## 2. Dataset Composition & Split Statistics

| Dataset Split | Image Count | Label File Count | Total Annotations | Split Ratio | Average Box Area (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | 4,200 | 4,200 | 4,200 | 70.0% | 1.68% |
| **Validation** | 1,200 | 1,200 | 1,200 | 20.0% | 1.70% |
| **Test** | 600 | 600 | 600 | 10.0% | 1.66% |
| **Total** | **6,000** | **6,000** | **6,000** | **100.0%** | **1.68%** |

*Note: Every image contains exactly one primary traffic sign instance, preventing multi-label clutter while accurately simulating vehicle line-of-sight navigation.*

---

## 3. Class Distribution Breakdown

The dataset defines 6 operational road signs essential for autonomous navigation:

| Class ID | Class Name | Car Action Trigger | Train Count | Valid Count | Test Count | Total Count | Class Share (%) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **0** | `left_turn` | Turn Left (Differential steer) | 700 | 200 | 100 | **1,000** | 16.67% |
| **1** | `straight_ahead` | Maintain Forward Motion | 694 | 198 | 108 | **1,000** | 16.67% |
| **2** | `right_turn` | Turn Right (Differential steer) | 726 | 202 | 72 | **1,000** | 16.67% |
| **3** | `dead_end` | Stop & Reverse / Re-route | 673 | 223 | 104 | **1,000** | 16.67% |
| **4** | `no_entry` | Immediate Stop / Forbid Entry | 697 | 194 | 109 | **1,000** | 16.67% |
| **5** | `stop` | Complete Halt (Active brake) | 710 | 183 | 107 | **1,000** | 16.67% |
| **Total** | — | — | **4,200** | **1,200** | **600** | **6,000** | **100.00%** |

### Class Balance Assessment:
- The maximum deviation from perfect parity (1,000 per class) across the entire 6,000 image corpus is **0.00%** (exactly 1,000 instances per class across the dataset).
- Train/Val/Test splits preserve near-uniform balance across all 6 classes.

---

## 4. Image Properties & Spatial Characteristics

1. **Resolution:** Uniform **640 × 640 pixels**, 3 channels (RGB).
2. **Color Space & Dynamic Range:** Standard sRGB 24-bit color. Images feature diverse lighting conditions (direct daylight, overcast, shaded, artificial indoor lighting, angle perspectives).
3. **Bounding Box Characteristics:**
   - Coordinate format: Normalized YOLO format `<class_id> <x_center> <y_center> <width> <height>`.
   - Bounding box normalized width ($w$) range: $0.05 \le w \le 0.35$ (median: $0.128$).
   - Bounding box normalized height ($h$) range: $0.05 \le h \le 0.35$ (median: $0.131$).
   - Mean box area: **1.68% of total frame area** (corresponds to an object size of approximately $82 \times 84$ pixels on a $640 \times 640$ canvas), accurately reflecting typical vehicle-mounted camera standoff distances (1.0 to 3.5 meters).
4. **Spatial Distribution:** Signs appear primarily centered horizontally within $0.25 \le x \le 0.75$ and vertically in the upper two-thirds of the image frame ($0.15 \le y \le 0.65$), matching road perspective geometry.

---

## 5. Dataset Validation & Integrity Checks

An exhaustive file-level integrity check verified:
- **Corrupt Image Check:** 0 corrupted or unreadable images.
- **Missing Label Check:** 0 images without corresponding `.txt` file.
- **Orphan Label Check:** 0 label files without corresponding `.jpg` image.
- **Coordinate Out-of-Bounds:** 0 bounding box coordinates $<0.0$ or $>1.0$.
- **Zero-Area Box Check:** 0 bounding boxes with width $\le 0$ or height $\le 0$.
- **Class Index Bounds:** All class indices strictly in $\{0, 1, 2, 3, 4, 5\}$.

---

## 6. Format Compatibility & Conversion Plan

The dataset is currently stored exclusively in YOLO text format:
```
<dataset_root>/
  train/images/*.jpg
  train/labels/*.txt
  valid/images/*.jpg
  valid/labels/*.txt
  test/images/*.jpg
  test/labels/*.txt
```

### Conversion Requirement for Non-YOLO Architectures:
To train and evaluate alternative detector architectures:
- **EfficientDet-Lite0 / Lite1:** Requires TensorFlow Records (`TFRecord`) or standard COCO JSON format.
- **SSD MobileNetV2 (TensorFlow / MediaPipe):** Requires COCO JSON or Pascal VOC XML format.
- **NanoDet-Plus / PP-PicoDet:** Requires standard COCO JSON format (`annotations/instances_train.json`, `instances_val.json`).

### Tool to Provide:
A dedicated conversion utility (`yolo_to_coco.py`) must be provided to convert the existing dataset into valid COCO 1.0 JSON format with category IDs mapping directly to the 6 traffic sign classes without modifying or duplicating the original dataset images.
