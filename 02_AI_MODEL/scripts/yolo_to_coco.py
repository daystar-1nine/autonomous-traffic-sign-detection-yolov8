#!/usr/bin/env python3
"""
YOLO to COCO Dataset Converter
Autonomous AI Traffic Sign Detection Car
Converts YOLO-format annotations (.txt) into standard COCO 1.0 JSON format
for training and evaluating non-YOLO models (EfficientDet-Lite, SSD MobileNet, NanoDet, PicoDet).
"""

import os
import sys
import glob
import json
import argparse
from PIL import Image
from collections import Counter
from datetime import datetime

CLASS_NAMES = [
    "left_turn",
    "straight_ahead",
    "right_turn",
    "dead_end",
    "no_entry",
    "stop"
]

def convert_split(dataset_dir, split, output_dir):
    """
    Converts a single dataset split (train, valid, test) to COCO JSON format.
    """
    img_dir = os.path.join(dataset_dir, split, "images")
    lbl_dir = os.path.join(dataset_dir, split, "labels")

    if not os.path.isdir(img_dir) or not os.path.isdir(lbl_dir):
        print(f"[WARN] Split '{split}' not found at {img_dir}. Skipping.")
        return None

    image_extensions = ("*.jpg", "*.jpeg", "*.png", "*.bmp")
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(img_dir, ext)))
    image_paths.sort()

    print(f"[*] Processing split '{split}': Found {len(image_paths)} images...")

    categories = [
        {"id": i, "name": name, "supercategory": "traffic_sign"}
        for i, name in enumerate(CLASS_NAMES)
    ]

    images_coco = []
    annotations_coco = []
    annotation_id = 1
    class_counts = Counter()

    for img_id, img_path in enumerate(image_paths, start=1):
        filename = os.path.basename(img_path)
        base_name, _ = os.path.splitext(filename)
        lbl_path = os.path.join(lbl_dir, base_name + ".txt")

        # Fast dimension extraction
        try:
            with Image.open(img_path) as img:
                width, height = img.size
        except Exception as e:
            print(f"[ERR] Failed to read {img_path}: {e}")
            continue

        images_coco.append({
            "id": img_id,
            "file_name": filename,
            "width": width,
            "height": height,
            "date_captured": datetime.now().isoformat()
        })

        if not os.path.exists(lbl_path):
            continue

        with open(lbl_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                try:
                    cls_id = int(parts[0])
                    x_c = float(parts[1])
                    y_c = float(parts[2])
                    w_norm = float(parts[3])
                    h_norm = float(parts[4])
                except ValueError:
                    continue

                if cls_id < 0 or cls_id >= len(CLASS_NAMES):
                    continue

                # Convert YOLO normalized (x_center, y_center, w, h) to COCO pixel (x_min, y_min, w, h)
                abs_w = w_norm * width
                abs_h = h_norm * height
                abs_x = (x_c * width) - (abs_w / 2.0)
                abs_y = (y_c * height) - (abs_h / 2.0)

                # Clamp to valid image boundaries
                abs_x = max(0.0, min(float(width), abs_x))
                abs_y = max(0.0, min(float(height), abs_y))
                abs_w = max(0.0, min(float(width - abs_x), abs_w))
                abs_h = max(0.0, min(float(height - abs_y), abs_h))
                area = abs_w * abs_h

                annotations_coco.append({
                    "id": annotation_id,
                    "image_id": img_id,
                    "category_id": cls_id,
                    "bbox": [round(abs_x, 2), round(abs_y, 2), round(abs_w, 2), round(abs_h, 2)],
                    "area": round(area, 2),
                    "segmentation": [],
                    "iscrowd": 0
                })
                annotation_id += 1
                class_counts[cls_id] += 1

    coco_data = {
        "info": {
            "description": "Autonomous Car Traffic Sign Dataset (COCO 1.0 Format)",
            "version": "2.0",
            "year": 2026,
            "contributor": "Autonomous Vehicle Vision Team",
            "date_created": datetime.now().strftime("%Y-%m-%d")
        },
        "licenses": [{"id": 1, "name": "Proprietary", "url": "N/A"}],
        "categories": categories,
        "images": images_coco,
        "annotations": annotations_coco
    }

    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"instances_{split}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(coco_data, f, indent=2)

    print(f"[OK] Split '{split}' complete: {len(images_coco)} images, {len(annotations_coco)} annotations -> {out_file}")
    for cid, cname in enumerate(CLASS_NAMES):
        print(f"    - Category {cid} ({cname}): {class_counts[cid]} annotations")

    return out_file

def main():
    parser = argparse.ArgumentParser(description="Convert YOLO dataset to COCO JSON format.")
    parser.add_argument("--dataset-dir", default="dataset", help="Path to YOLO dataset root.")
    parser.add_argument("--output-dir", default="dataset/annotations", help="Destination directory for COCO JSON files.")
    parser.add_argument("--splits", nargs="+", default=["train", "valid", "test"], help="Splits to convert.")
    args = parser.parse_args()

    print("=================================================================")
    print("  AUTONOMOUS CAR: YOLO TO COCO CONVERSION UTILITY")
    print("=================================================================")
    print(f"Dataset root: {os.path.abspath(args.dataset_dir)}")
    print(f"Output annotations: {os.path.abspath(args.output_dir)}")
    print(f"Target splits: {args.splits}")
    print("-----------------------------------------------------------------")

    for split in args.splits:
        convert_split(args.dataset_dir, split, args.output_dir)

    print("\n[SUCCESS] All requested splits converted to COCO format.")

if __name__ == "__main__":
    main()
