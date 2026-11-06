"""
Retrain YOLOv8n on Robust Multi-Scale Traffic Signs Dataset
Features:
- Zero horizontal flip (fliplr=0.0) to prevent left/right arrow confusion
- Multi-scale and position-invariant feature learning
- Windows-safe workers=0 to eliminate CUDA pin_memory mapping collisions
- RAM Caching (cache=True) for blazing-fast 6s/epoch training on RTX 5060
- Automatic ONNX export and Android assets deployment
"""

import sys
import shutil
from pathlib import Path
import torch
from ultralytics import YOLO

def main():
    print("=======================================================")
    print("  YOLOv8n TRAFFIC SIGN DETECTION - RETRAINING PIPELINE  ")
    print("=======================================================")

    device = 0 if torch.cuda.is_available() else "cpu"
    if torch.cuda.is_available():
        print(f"[INFO] Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("[WARN] GPU not detected, falling back to CPU")

    data_yaml = Path("dataset_robust/data.yaml").resolve()
    if not data_yaml.is_file():
        raise FileNotFoundError(f"data.yaml not found at: {data_yaml}")

    # Use pretrained yolov8n.pt for clean feature extraction
    base_model_path = "yolov8n.pt"
    print(f"[INFO] Initializing YOLOv8n from: {base_model_path}")
    model = YOLO(base_model_path)

    # Train for 20 epochs with workers=0 and cache=True
    print("[INFO] Starting training with workers=0, cache=True, fliplr=0.0, mosaic=1.0...")
    results = model.train(
        data=str(data_yaml),
        epochs=20,
        batch=16,
        imgsz=640,
        device=device,
        workers=0,    # Windows CUDA safety: Avoids multi-process pin_memory mapping conflict
        cache=True,   # Cache images in RAM for maximum GPU throughput
        name="robust_yolov8n",
        project="runs/train",
        exist_ok=True,
        fliplr=0.0,   # CRITICAL: Do NOT flip horizontally!
        flipud=0.0,   # CRITICAL: Do NOT flip vertically!
        mosaic=1.0,   # 4-image mosaic composition
        scale=0.5,    # Random scale variation +/- 50%
        degrees=10.0, # Random rotation +/- 10 degrees
        translate=0.1,# Random translation +/- 10%
        patience=15,
        plots=True,
        save=True,
        verbose=True
    )

    print("\n[INFO] Training finished! Locating best checkpoint...")
    save_dir = Path(model.trainer.save_dir) if hasattr(model, 'trainer') and model.trainer else Path("runs/train/robust_yolov8n")
    best_pt = save_dir / "weights" / "best.pt"
    if not best_pt.is_file():
        matches = list(Path("runs").rglob("best.pt"))
        if matches:
            best_pt = sorted(matches, key=lambda p: p.stat().st_mtime)[-1]
        else:
            raise FileNotFoundError("Could not find best.pt!")

    print(f"[SUCCESS] Best weights found at: {best_pt}")

    # Validate best model
    best_model = YOLO(str(best_pt))
    print("\n[INFO] Running Validation on dataset_robust/valid...")
    metrics = best_model.val(data=str(data_yaml), split="val", device=device, workers=0)
    print(f"mAP50: {metrics.box.map50:.4f}, mAP50-95: {metrics.box.map:.4f}")

    # Export to ONNX
    print("\n[INFO] Exporting to ONNX format (simplify=True, opset=12)...")
    exported_onnx_path = best_model.export(format="onnx", dynamic=False, simplify=True, opset=12)
    print(f"[SUCCESS] ONNX model exported to: {exported_onnx_path}")

    # Deploy to required destinations
    destinations = [
        Path("android-app/app/src/main/assets/yolov8n.onnx"),
        Path("02_AI_MODEL/exports/yolov8n_traffic_signs.onnx"),
        Path("models/weights/best_yolov8n.onnx"),
        Path("models/exported/yolov8n_traffic_signs.onnx"),
    ]

    for dst in destinations:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(exported_onnx_path), str(dst))
        print(f" -> Deployed ONNX to: {dst} ({dst.stat().st_size} bytes)")

    # Also update best_yolov8n.pt
    shutil.copy(str(best_pt), "models/weights/best_yolov8n.pt")
    if Path("02_AI_MODEL/weights").exists():
        shutil.copy(str(best_pt), "02_AI_MODEL/weights/best_yolov8n.pt")
    print(f" -> Updated PyTorch weights in models/weights/best_yolov8n.pt")

    print("\n=======================================================")
    print("[ALL DONE] Model retrained, validated, exported, and deployed!")
    print("=======================================================")


if __name__ == "__main__":
    main()
