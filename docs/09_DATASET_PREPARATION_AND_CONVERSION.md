# 09. DATASET PREPARATION & FORMAT CONVERSION
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Dataset Structure & Traffic Sign Ontology

The dataset located at `dataset/` contains **6,000 images** meticulously annotated across 6 operational classes:

```
dataset/
├── train/
│   ├── images/   (4,200 images, 640x640 JPG)
│   └── labels/   (4,200 text files)
├── valid/
│   ├── images/   (1,200 images, 640x640 JPG)
│   └── labels/   (1,200 text files)
├── test/
│   ├── images/   (600 images, 640x640 JPG)
│   └── labels/   (600 text files)
├── data.yaml     (YOLO dataset configuration)
└── classes.txt   (List of class names)
```

### Class Definitions:
- **0: `left_turn`** — Approaching left turn curve. Trigger: Differential left turn.
- **1: `straight_ahead`** — Clear open road. Trigger: Maintain forward cruise.
- **2: `right_turn`** — Approaching right turn curve. Trigger: Differential right turn.
- **3: `dead_end`** — Road termination. Trigger: Halt, reverse, or re-route.
- **4: `no_entry`** — Forbidden entry road. Trigger: Immediate active brake.
- **5: `stop`** — Red regulatory stop sign. Trigger: Immediate active brake for 3.0 seconds.

---

## 2. YOLO Text Format Standard

Each `.txt` file contains one or more rows representing bounding boxes formatted as:
```
<class_id> <x_center> <y_center> <width> <height>
```
All coordinate values are normalized between `0.0` and `1.0` relative to image dimensions ($640 \times 640$).

Example:
```
5 0.5125 0.3854 0.1420 0.1650
```
This specifies class 5 (`stop`), centered at $x=51.25\%$, $y=38.54\%$, with a width of $14.20\%$ and height of $16.50\%$ of the image frame.

---

## 3. Converting YOLO Format to COCO JSON (`yolo_to_coco.py`)

Non-YOLO architectures (such as EfficientDet-Lite0, SSD MobileNetV2, NanoDet-Plus, PP-PicoDet) require annotations in standard **COCO 1.0 JSON format**.

A dedicated conversion script is located at `ai-training/dataset-tools/yolo_to_coco.py`:

```bash
# Run the conversion utility on all three splits
python ai-training/dataset-tools/yolo_to_coco.py --dataset-dir dataset --output-dir dataset/annotations
```

### Generated Artifacts:
- `dataset/annotations/instances_train.json` (4,200 images, 4,200 annotations)
- `dataset/annotations/instances_valid.json` (1,200 images, 1,200 annotations)
- `dataset/annotations/instances_test.json` (600 images, 600 annotations)

The converted COCO files include category metadata, normalized pixel bounding box calculations (`[x_min, y_min, width, height]`), and area calculations, making them directly consumable by TensorFlow Model Maker, MMDetection, or PaddleDetection pipelines.
