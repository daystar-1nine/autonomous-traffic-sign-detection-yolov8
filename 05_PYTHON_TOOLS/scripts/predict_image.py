"""
Single and Batch Image Inference Pipeline for YOLOv8 Traffic Sign Detection.
Autonomous AI Car Project - 05_PYTHON_TOOLS
"""

import argparse
import sys
import os
import glob
from pathlib import Path
from typing import List
import cv2
from ultralytics import YOLO

try:
    from utils import (
        get_device,
        get_project_root,
        load_model,
        draw_detection_box,
        save_detection_summary,
        is_valid_sign_box,
        CLASS_NAMES,
    )
except ImportError:
    from .utils import (
        get_device,
        get_project_root,
        load_model,
        draw_detection_box,
        save_detection_summary,
        is_valid_sign_box,
        CLASS_NAMES,
    )

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run YOLOv8 Traffic Sign Detection on Single or Multiple Images"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="dataset/sample_signs",
        help="Path to an image file or directory of images (default: dataset/sample_signs)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="02_AI_MODEL/weights/best_yolov8n.pt",
        help="Path to trained model weights (default: 02_AI_MODEL/weights/best_yolov8n.pt)",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.60,
        help="Confidence threshold (0.0 to 1.0, default: 0.60 for strict sign detection)",
    )
    parser.add_argument(
        "--filter-geometry",
        action="store_true",
        default=True,
        help="Enable geometric and aspect ratio filtering to suppress background false positives",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.45,
        help="NMS IoU threshold (0.0 to 1.0, default: 0.45)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Image size in pixels (default: 640)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (e.g., 'cpu', 'cuda:0'). Defaults to auto-detect.",
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        default="07_REPORTS/predictions",
        help="Directory to save annotated images (default: 07_REPORTS/predictions)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display prediction windows interactively",
    )
    return parser.parse_args()


def collect_images(source_path: Path) -> List[Path]:
    """Finds all valid image files from a given file path or directory."""
    if source_path.is_file():
        if source_path.suffix.lower() in IMAGE_EXTENSIONS:
            return [source_path]
        raise ValueError(f"File {source_path} is not a supported image format.")

    if source_path.is_dir():
        found = {p.resolve(): p for p in source_path.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS}
        return sorted(found.values())

    # Check if wildcard string
    wildcard_matches = [Path(p) for p in glob.glob(str(source_path))]
    valid_matches = {p.resolve(): p for p in wildcard_matches if p.suffix.lower() in IMAGE_EXTENSIONS}
    if valid_matches:
        return sorted(valid_matches.values())

    raise FileNotFoundError(f"Source image(s) not found at: {source_path}")


def predict_images(args):
    root = get_project_root()
    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = root / source_path

    images = collect_images(source_path)
    if not images:
        print(f"[WARN] No valid images found in: {source_path}")
        return []

    save_dir = Path(args.save_dir)
    if not save_dir.is_absolute():
        save_dir = root / save_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    model = load_model(args.model, device=args.device)
    device = get_device(args.device)

    print("\n" + "=" * 65)
    print(f" YOLOV8 IMAGE DETECTION PIPELINE")
    print(f" Total Images: {len(images)}")
    print(f" Model: {args.model} | Device: {device}")
    print(f" Conf Threshold: {args.conf} | IoU Threshold: {args.iou}")
    print(f" Output Directory: {save_dir}")
    print("=" * 65 + "\n")

    all_detections = []

    for idx, img_path in enumerate(images, start=1):
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"[{idx}/{len(images)}] [WARN] Failed to read {img_path.name}. Skipping.")
            continue

        results = model.predict(
            source=image,
            conf=args.conf,
            iou=args.iou,
            imgsz=args.imgsz,
            device=device,
            verbose=False,
        )

        r = results[0]
        detected_objects = []

        if r.boxes is not None and len(r.boxes) > 0:
            for box in r.boxes:
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                xyxy = box.xyxy.tolist()[0]

                # Check geometric validity if enabled
                if getattr(args, "filter_geometry", True):
                    if not is_valid_sign_box(xyxy, image.shape):
                        continue

                cls_name = model.names.get(cls_id, CLASS_NAMES.get(cls_id, f"Class {cls_id}"))

                # Draw custom formatted bounding box
                draw_detection_box(
                    image=image,
                    xyxy=xyxy,
                    class_id=cls_id,
                    confidence=conf,
                    class_name=cls_name,
                )

                detected_objects.append({
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "confidence": round(conf, 4),
                    "bbox_xyxy": [round(c, 2) for c in xyxy],
                })

        # Save annotated image
        out_filename = f"pred_{img_path.name}"
        out_filepath = save_dir / out_filename
        cv2.imwrite(str(out_filepath), image)

        all_detections.append({
            "image": img_path.name,
            "detections_count": len(detected_objects),
            "detections": detected_objects,
        })

        det_str = ", ".join([f"{d['class_name']} ({d['confidence']*100:.1f}%)" for d in detected_objects]) or "None"
        print(f"[{idx}/{len(images)}] {img_path.name} -> Detections: {det_str}")

        if args.show:
            cv2.imshow("Traffic Sign Detection", image)
            key = cv2.waitKey(0) & 0xFF
            if key == 27 or key == ord("q"):
                print("[INFO] Display terminated by user.")
                break

    if args.show:
        cv2.destroyAllWindows()

    # Save structured detection summary
    summary_file = save_dir / "detections_summary.json"
    save_detection_summary(all_detections, summary_file)

    print("\n" + "=" * 65)
    print(f" Inference complete! Annotated images saved to: {save_dir}")
    print("=" * 65 + "\n")

    return all_detections


def main():
    args = parse_args()
    try:
        predict_images(args)
    except Exception as e:
        print(f"\n[ERROR] Image prediction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
