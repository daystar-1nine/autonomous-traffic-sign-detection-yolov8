"""
Evaluation and Benchmarking Pipeline for YOLOv8 Traffic Sign Detection.
Computes Precision, Recall, mAP@50, mAP@50-95, per-class breakdown,
confusion matrix, and saves validation visualizations.
"""

import argparse
import sys
import json
from pathlib import Path
from ultralytics import YOLO

# Add parent directory to path to allow absolute package imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.utils import get_device, get_project_root, CLASS_NAMES


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate YOLOv8 Traffic Sign Detection Model on Test/Val Split"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/best.pt",
        help="Path to trained model weights (default: models/best.pt)",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="configs/data.yaml",
        help="Path to dataset YAML file (default: configs/data.yaml)",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        choices=["test", "val"],
        help="Dataset split to evaluate (default: test)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Image size in pixels (default: 640)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Evaluation batch size (default: 16)",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold for evaluation (default: 0.25)",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.6,
        help="NMS IoU threshold for evaluation (default: 0.6)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (e.g., '0', 'cpu', 'cuda:0'). Defaults to auto-detect.",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="outputs/evaluation",
        help="Directory to save evaluation plots and metrics (default: outputs/evaluation)",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="test_benchmark",
        help="Subdirectory name for evaluation output",
    )
    return parser.parse_args()


def evaluate(args):
    root = get_project_root()
    model_path = Path(args.model)
    if not model_path.is_absolute():
        model_path = root / model_path

    if not model_path.is_file():
        raise FileNotFoundError(
            f"Model file not found at: {model_path}\n"
            f"Ensure models/best.pt exists or pass a valid model path."
        )

    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = root / data_path

    if not data_path.is_file():
        raise FileNotFoundError(f"Dataset config not found at: {data_path}")

    project_dir = Path(args.project)
    if not project_dir.is_absolute():
        project_dir = root / project_dir

    device = get_device(args.device)

    print("\n" + "=" * 70)
    print(" YOLOV8 TRAFFIC SIGN BENCHMARK EVALUATION")
    print(f" Model: {model_path}")
    print(f" Dataset YAML: {data_path}")
    print(f" Target Split: {args.split.upper()}")
    print(f" Device: {device} | ImgSz: {args.imgsz} | Batch: {args.batch}")
    print(f" Confidence Threshold: {args.conf} | IoU Threshold: {args.iou}")
    print("=" * 70 + "\n")

    model = YOLO(str(model_path))

    metrics = model.val(
        data=str(data_path),
        split=args.split,
        imgsz=args.imgsz,
        batch=args.batch,
        conf=args.conf,
        iou=args.iou,
        device=device,
        project=str(project_dir),
        name=args.name,
        plots=True,
        save_json=True,
        verbose=True,
    )

    # Extract overall metrics
    precision = float(metrics.box.mp)
    recall = float(metrics.box.mr)
    map50 = float(metrics.box.map50)
    map50_95 = float(metrics.box.map)

    print("\n" + "=" * 70)
    print(f" OVERALL BENCHMARK RESULTS ({args.split.upper()} SPLIT)")
    print("=" * 70)
    print(f" Precision (P)      : {precision * 100:.2f}% ({precision:.4f})")
    print(f" Recall (R)         : {recall * 100:.2f}% ({recall:.4f})")
    print(f" mAP @ 0.50         : {map50 * 100:.2f}% ({map50:.4f})")
    print(f" mAP @ 0.50:0.95    : {map50_95 * 100:.2f}% ({map50_95:.4f})")
    print("-" * 70)

    # Per-class metrics table
    class_metrics = {}
    print(f"{'Class ID':<10} {'Class Name':<18} {'Precision':<12} {'Recall':<12} {'mAP@50':<12} {'mAP@50-95':<12}")
    print("-" * 70)

    for i, c in enumerate(metrics.box.ap_class_index):
        cls_id = int(c)
        cls_name = model.names.get(cls_id, CLASS_NAMES.get(cls_id, f"class_{cls_id}"))
        p = float(metrics.box.p[i])
        r = float(metrics.box.r[i])
        ap50 = float(metrics.box.ap50[i])
        ap = float(metrics.box.ap[i])

        class_metrics[cls_name] = {
            "class_id": cls_id,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "mAP50": round(ap50, 4),
            "mAP50_95": round(ap, 4),
        }

        print(
            f"{cls_id:<10} {cls_name:<18} "
            f"{p * 100:>6.2f}% ({p:.3f})  "
            f"{r * 100:>6.2f}% ({r:.3f})  "
            f"{ap50 * 100:>6.2f}% ({ap50:.3f})  "
            f"{ap * 100:>6.2f}% ({ap:.3f})"
        )

    print("=" * 70)

    # Export structured metrics JSON
    summary = {
        "split": args.split,
        "model": str(model_path.name),
        "overall": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "mAP50": round(map50, 4),
            "mAP50_95": round(map50_95, 4),
        },
        "per_class": class_metrics,
        "plots_saved_to": str(project_dir / args.name),
    }

    output_json = project_dir / args.name / "metrics_summary.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[INFO] Detailed metrics JSON saved to: {output_json}")
    print(f"[INFO] Evaluation plots saved to: {project_dir / args.name}")
    print("=" * 70 + "\n")

    return summary


def main():
    args = parse_args()
    try:
        evaluate(args)
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
