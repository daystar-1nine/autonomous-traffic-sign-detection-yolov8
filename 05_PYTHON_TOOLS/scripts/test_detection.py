"""
Static & Batch Traffic Sign Detection Test Tool
Autonomous AI Car Project
Tests image inference with geometric false-positive filtering.
"""

import argparse
import sys
from pathlib import Path
import cv2
from ultralytics import YOLO

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils import get_device, is_valid_sign_box, CLASS_NAMES, CLASS_COLORS


def parse_args():
    parser = argparse.ArgumentParser(description="Test Traffic Sign Detection on Images")
    parser.add_argument("--source", type=str, default="dataset/sample_signs", help="Image file or directory")
    parser.add_argument("--model", type=str, default="02_AI_MODEL/weights/best_yolov8n.pt", help="Model weights")
    parser.add_argument("--conf", type=float, default=0.60, help="Confidence threshold")
    parser.add_argument("--output-dir", type=str, default="outputs/predictions/test_tool", help="Save directory")
    return parser.parse_args()


def main():
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.is_file():
        raise FileNotFoundError(f"Model not found at: {model_path.resolve()}")

    device = get_device()
    model = YOLO(str(model_path))

    source_path = Path(args.source)
    if source_path.is_file():
        images = [source_path]
    elif source_path.is_dir():
        images = list(source_path.glob("*.jpg")) + list(source_path.glob("*.png"))
    else:
        raise FileNotFoundError(f"Source not found: {source_path}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Running detection on {len(images)} images using {model_path.name}...")

    for img_path in images:
        frame = cv2.imread(str(img_path))
        if frame is None:
            continue
        h, w = frame.shape[:2]

        results = model.predict(source=frame, conf=args.conf, iou=0.45, device=device, verbose=False)[0]

        detected_count = 0
        if results.boxes is not None and len(results.boxes) > 0:
            for box in results.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].cpu().numpy().astype(int)

                if is_valid_sign_box(xyxy, (h, w), conf, min_conf=args.conf):
                    detected_count += 1
                    color = CLASS_COLORS.get(cls_id, (0, 255, 0))
                    name = CLASS_NAMES.get(cls_id, f"sign_{cls_id}")

                    cv2.rectangle(frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), color, 3)
                    label = f"{name} {conf:.1%}"
                    cv2.putText(frame, label, (xyxy[0], max(20, xyxy[1] - 8)), cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 2)

        out_file = out_dir / f"pred_{img_path.name}"
        cv2.imwrite(str(out_file), frame)
        print(f" - {img_path.name:<30} -> Detected {detected_count} valid signs -> Saved: {out_file.name}")

    print(f"\n[COMPLETED] Annotated outputs saved to: {out_dir}\n")


if __name__ == "__main__":
    main()
