"""
Training pipeline for YOLOv8 Traffic Sign Detection.
Supports configurable hyperparameters, device fallback, checkpoint resumption,
and structured logging for both local environments and Google Colab.
"""

import argparse
import sys
from pathlib import Path
import yaml
from ultralytics import YOLO

# Add parent directory to path to allow absolute package imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.utils import get_device, get_project_root


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train YOLOv8 on Traffic Signs Dataset (Autonomous Car)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/yolov8n.pt",
        help="Initial model weights (default: models/yolov8n.pt or yolov8n.pt)",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="configs/data.yaml",
        help="Path to dataset YAML file (default: configs/data.yaml)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs (default: 100)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Batch size (default: 16)",
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
        help="Compute device (e.g., '0', 'cpu', 'cuda:0'). Defaults to auto-detect.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Dataloader worker processes (default: 2)",
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=0,
        help="Early stopping patience in epochs (0 = disabled, default: 0)",
    )
    parser.add_argument(
        "--optimizer",
        type=str,
        default="auto",
        choices=["SGD", "Adam", "AdamW", "NAdam", "RAdam", "RMSProp", "auto"],
        help="Optimizer choice (default: auto)",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="runs/train",
        help="Project directory to save training runs (default: runs/train)",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="traffic_signs_yolov8n",
        help="Name of the training run subfolder",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Path to checkpoint (e.g., last.pt) to resume interrupted training",
    )
    parser.add_argument(
        "--exist-ok",
        action="store_true",
        help="Overwrite existing run directory if it exists",
    )
    return parser.parse_args()


def train(args):
    root = get_project_root()
    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = root / data_path

    if not data_path.is_file():
        raise FileNotFoundError(
            f"Dataset configuration YAML not found at: {data_path}\n"
            f"Please verify configs/data.yaml exists."
        )

    # Validate YAML content
    with open(data_path, "r", encoding="utf-8") as f:
        data_cfg = yaml.safe_load(f)
    print(f"[INFO] Loaded dataset YAML: {data_path}")
    print(f"[INFO] Classes configured ({data_cfg.get('nc', 'unknown')}): {data_cfg.get('names')}")

    device = get_device(args.device)
    print(f"[INFO] Training execution device: {device}")

    # Resume mode vs fresh training
    if args.resume:
        resume_path = Path(args.resume)
        if not resume_path.is_absolute():
            resume_path = root / resume_path
        if not resume_path.is_file():
            raise FileNotFoundError(f"Resume checkpoint not found at: {resume_path}")
        print(f"[INFO] Resuming training from checkpoint: {resume_path}")
        model = YOLO(str(resume_path))
        results = model.train(resume=True)
        return results

    # Initial model weights resolution
    model_path = Path(args.model)
    if not model_path.is_absolute():
        potential_path = root / model_path
        if potential_path.is_file():
            model_path = potential_path
        else:
            model_path = Path(args.model)  # Let ultralytics download if standard name

    print(f"[INFO] Initializing YOLO with weights: {model_path}")
    model = YOLO(str(model_path))

    project_dir = Path(args.project)
    if not project_dir.is_absolute():
        project_dir = root / project_dir

    print("\n" + "=" * 65)
    print(f" STARTING YOLOV8 TRAINING: {args.name}")
    print(f" Epochs: {args.epochs} | Batch: {args.batch} | ImgSz: {args.imgsz}")
    print(f" Optimizer: {args.optimizer} | Patience: {args.patience}")
    print(f" Project Dir: {project_dir}")
    print("=" * 65 + "\n")

    results = model.train(
        data=str(data_path),
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=device,
        workers=args.workers,
        patience=args.patience,
        optimizer=args.optimizer,
        project=str(project_dir),
        name=args.name,
        exist_ok=args.exist_ok,
        save=True,
        plots=True,
        verbose=True,
    )

    print("\n" + "=" * 65)
    print(" TRAINING COMPLETED SUCCESSFULLY")
    print(f" Best weights saved to: {project_dir / args.name / 'weights' / 'best.pt'}")
    print(f" Last weights saved to: {project_dir / args.name / 'weights' / 'last.pt'}")
    print("=" * 65 + "\n")

    return results


def main():
    args = parse_args()
    try:
        train(args)
    except KeyboardInterrupt:
        print("\n[INFO] Training manually interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Training failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
