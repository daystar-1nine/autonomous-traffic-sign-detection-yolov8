"""
Train YOLOv8s (Small - High Capacity) on Robust Multi-Scale Dataset
Compares against YOLOv8n to identify the ultimate best model for traffic sign detection.
"""

from pathlib import Path
import torch
from ultralytics import YOLO

def main():
    print("=======================================================")
    print("  YOLOv8s (SMALL) TRAFFIC SIGN DETECTION PIPELINE      ")
    print("=======================================================")

    device = 0 if torch.cuda.is_available() else "cpu"
    data_yaml = Path("dataset_robust/data.yaml").resolve()

    print("[INFO] Initializing YOLOv8s from yolov8s.pt...")
    model = YOLO("yolov8s.pt")

    results = model.train(
        data=str(data_yaml),
        epochs=20,
        batch=16,
        imgsz=640,
        device=device,
        workers=0,
        cache=True,
        name="robust_yolov8s",
        project="runs/train",
        exist_ok=True,
        fliplr=0.0,
        flipud=0.0,
        mosaic=1.0,
        scale=0.5,
        degrees=10.0,
        translate=0.1,
        patience=15,
        plots=True,
        save=True,
        verbose=True
    )

    save_dir = Path(model.trainer.save_dir) if hasattr(model, 'trainer') and model.trainer else Path("runs/train/robust_yolov8s")
    best_pt = save_dir / "weights" / "best.pt"
    print(f"[SUCCESS] Best YOLOv8s weights saved at: {best_pt}")

    # Validate
    best_model = YOLO(str(best_pt))
    metrics = best_model.val(data=str(data_yaml), split="val", device=device, workers=0)
    print(f"\n[METRICS] YOLOv8s mAP50: {metrics.box.map50:.4f}, mAP50-95: {metrics.box.map:.4f}")

    # Export ONNX
    onnx_path = best_model.export(format="onnx", dynamic=False, simplify=True, opset=12)
    print(f"[SUCCESS] Exported ONNX to: {onnx_path}")

if __name__ == "__main__":
    main()
