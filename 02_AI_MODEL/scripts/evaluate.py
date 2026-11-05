"""
Model Evaluation and Test Split Benchmarking Script
Autonomous AI Car Project
"""

import argparse
import json
import sys
from pathlib import Path
from ultralytics import YOLO

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils import get_device, CLASS_NAMES


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate YOLO Model on Dataset Split")
    parser.add_argument("--model", type=str, default="02_AI_MODEL/weights/best_yolov8n.pt", help="Path to weights")
    parser.add_argument("--data", type=str, default="02_AI_MODEL/dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--split", type=str, default="test", choices=["train", "val", "test"], help="Dataset split")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--device", type=str, default=None, help="Device (0 or cpu)")
    parser.add_argument("--output-dir", type=str, default="07_REPORTS/eval_results", help="Directory for results")
    return parser.parse_args()


def evaluate():
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.is_file():
        raise FileNotFoundError(f"Model not found at: {model_path.resolve()}")

    device = get_device(args.device)
    model = YOLO(str(model_path))

    print(f"\n[INFO] Evaluating {model_path.name} on split: '{args.split}'...")
    metrics = model.val(
        data=args.data,
        split=args.split,
        batch=args.batch,
        imgsz=args.imgsz,
        device=device,
        plots=True,
        save_json=True,
        project=args.output_dir,
        name=f"{model_path.stem}_{args.split}",
    )

    out_dir = Path(args.output_dir) / f"{model_path.stem}_{args.split}"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "model": model_path.name,
        "split": args.split,
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "mAP50": float(metrics.box.map50),
        "mAP50_95": float(metrics.box.map),
        "per_class": {},
    }

    print("\n" + "=" * 60)
    print(f" EVALUATION BENCHMARK: {model_path.name} on {args.split.upper()} SET")
    print("=" * 60)
    print(f" Precision (P)    : {summary['precision']:.4f} ({summary['precision']*100:.2f}%)")
    print(f" Recall (R)       : {summary['recall']:.4f} ({summary['recall']*100:.2f}%)")
    print(f" mAP @ 0.50       : {summary['mAP50']:.4f} ({summary['mAP50']*100:.2f}%)")
    print(f" mAP @ 0.50:0.95  : {summary['mAP50_95']:.4f} ({summary['mAP50_95']*100:.2f}%)")
    print("-" * 60)

    for i, cls_name in CLASS_NAMES.items():
        if i < len(metrics.box.maps):
            p_val = float(metrics.box.p[i]) if hasattr(metrics.box, "p") and len(metrics.box.p) > i else 0.0
            r_val = float(metrics.box.r[i]) if hasattr(metrics.box, "r") and len(metrics.box.r) > i else 0.0
            map50_val = float(metrics.box.all_ap[i, 0]) if hasattr(metrics.box, "all_ap") else float(metrics.box.maps[i])
            summary["per_class"][cls_name] = {
                "precision": p_val,
                "recall": r_val,
                "mAP50": map50_val,
            }
            print(f" Class {i} [{cls_name:<15}]: P={p_val:.3f} | R={r_val:.3f} | mAP50={map50_val:.4f}")

    json_path = out_dir / "metrics_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[SAVED] Benchmark summary written to: {json_path}")
    return summary


if __name__ == "__main__":
    evaluate()
