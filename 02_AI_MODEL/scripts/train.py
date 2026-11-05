"""
Model Training Script - YOLOv8 Traffic Sign Detection
Autonomous AI Car Project
"""

import argparse
import sys
from pathlib import Path
from ultralytics import YOLO

# Add root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils import get_device


def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLOv8 on Traffic Signs Dataset")
    parser.add_argument("--data", type=str, default="02_AI_MODEL/dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base model weights (yolov8n.pt, yolov8s.pt)")
    parser.add_argument("--epochs", type=int, default=60, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image resolution")
    parser.add_argument("--device", type=str, default=None, help="Device (e.g. 0 or cpu)")
    parser.add_argument("--name", type=str, default="yolov8_traffic_signs", help="Experiment name")
    parser.add_argument("--resume", type=str, default=None, help="Checkpoint to resume training")
    return parser.parse_args()


def train():
    args = parse_args()
    data_path = Path(args.data)
    if not data_path.is_file():
        raise FileNotFoundError(f"data.yaml not found at: {data_path.resolve()}")

    device = get_device(args.device)

    if args.resume:
        print(f"[INFO] Resuming training from checkpoint: {args.resume}")
        model = YOLO(args.resume)
        results = model.train(resume=True)
    else:
        print(f"[INFO] Initializing model: {args.model}")
        model = YOLO(args.model)
        results = model.train(
            data=str(data_path),
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
            device=device,
            name=args.name,
            project="runs/train",
            plots=True,
            verbose=True,
            patience=20,
            save=True,
        )

    print("\n[SUCCESS] Training completed!")
    print(f"Best weights saved to: runs/train/{args.name}/weights/best.pt")
    return results


if __name__ == "__main__":
    train()
