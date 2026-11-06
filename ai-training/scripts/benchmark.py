"""
Inference Latency & Mobile Benchmark Script
Autonomous AI Car Project
Measures: Preprocessing, Forward Pass, Postprocessing & FPS across devices.
"""

import argparse
import time
import sys
from pathlib import Path
import numpy as np
import torch
from ultralytics import YOLO

try:
    from utils import get_device
except ImportError:
    from .utils import get_device


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark Model Inference Latency")
    parser.add_argument("--model", type=str, default="02_AI_MODEL/weights/best_yolov8n.pt", help="Path to weights")
    parser.add_argument("--device", type=str, default=None, help="Device (cpu or 0)")
    parser.add_argument("--runs", type=int, default=100, help="Number of benchmark iterations")
    parser.add_argument("--imgsz", type=int, default=640, help="Frame resolution")
    return parser.parse_args()


def benchmark():
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.is_file():
        raise FileNotFoundError(f"Model not found at: {model_path.resolve()}")

    device = get_device(args.device)
    model = YOLO(str(model_path))

    # Synthetic dummy image (RGB 640x640)
    dummy_frame = np.random.randint(0, 255, (args.imgsz, args.imgsz, 3), dtype=np.uint8)

    print(f"\n[INFO] Starting benchmark for: {model_path.name} on {device}")
    print(f"Iterations: {args.runs} | Input Resolution: {args.imgsz}x{args.imgsz}")

    # Warmup
    print("[WARMUP] Running 10 warmup iterations...")
    for _ in range(10):
        _ = model.predict(source=dummy_frame, device=device, verbose=False, imgsz=args.imgsz)

    latencies = []
    print(f"[BENCHMARK] Executing {args.runs} timed runs...")
    for _ in range(args.runs):
        t0 = time.perf_counter()
        _ = model.predict(source=dummy_frame, device=device, verbose=False, imgsz=args.imgsz)
        dt = (time.perf_counter() - t0) * 1000.0
        latencies.append(dt)

    latencies = np.array(latencies)
    mean_ms = np.mean(latencies)
    p50_ms = np.median(latencies)
    p95_ms = np.percentile(latencies, 95)
    p99_ms = np.percentile(latencies, 99)
    min_ms = np.min(latencies)
    max_ms = np.max(latencies)
    fps = 1000.0 / mean_ms

    print("\n" + "=" * 60)
    print(f" LATENCY BENCHMARK REPORT: {model_path.name}")
    print("=" * 60)
    print(f" Device          : {device}")
    print(f" Average Latency : {mean_ms:.2f} ms")
    print(f" Median (P50)    : {p50_ms:.2f} ms")
    print(f" 95th Percentile : {p95_ms:.2f} ms")
    print(f" 99th Percentile : {p99_ms:.2f} ms")
    print(f" Min / Max       : {min_ms:.2f} ms / {max_ms:.2f} ms")
    print(f" Equivalent FPS  : {fps:.1f} FPS")
    print("=" * 60 + "\n")

    return {
        "model": model_path.name,
        "device": str(device),
        "mean_ms": mean_ms,
        "fps": fps,
        "p50_ms": p50_ms,
        "p95_ms": p95_ms,
    }


if __name__ == "__main__":
    benchmark()
