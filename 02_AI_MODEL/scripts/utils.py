"""
AI Model Utility Module - YOLOv8 Traffic Sign Detection
Autonomous AI Car Project
"""

import os
from pathlib import Path
from typing import Dict, Tuple, Optional, Union, List
import cv2
import numpy as np
import torch
from ultralytics import YOLO

CLASS_NAMES: Dict[int, str] = {
    0: "left_turn",
    1: "straight_ahead",
    2: "right_turn",
    3: "dead_end",
    4: "no_entry",
    5: "stop",
}

CLASS_COLORS: Dict[int, Tuple[int, int, int]] = {
    0: (255, 128, 0),    # Left Turn: Cyan/Sky Blue
    1: (0, 200, 0),      # Straight Ahead: Green
    2: (0, 165, 255),    # Right Turn: Orange
    3: (0, 215, 255),    # Dead End: Yellow
    4: (0, 69, 255),     # No Entry: Orange-Red
    5: (0, 0, 255),      # Stop: Red
}


def get_device(preferred_device: Optional[str] = None) -> str:
    """Selects the best available execution device (CUDA or CPU)."""
    if preferred_device:
        dev = str(preferred_device).lower().strip()
        if "cuda" in dev or dev in ("0", "1"):
            if torch.cuda.is_available():
                return preferred_device
            print("[WARN] CUDA requested but unavailable. Falling back to CPU.")
            return "cpu"
        return preferred_device

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"[INFO] CUDA GPU detected: {gpu_name}")
        return "cuda:0"

    print("[INFO] Using CPU execution.")
    return "cpu"


def load_model(weights_path: Union[str, Path], device: Optional[str] = None) -> YOLO:
    """Loads a YOLO model with file verification."""
    p = Path(weights_path)
    if not p.is_file():
        raise FileNotFoundError(f"Model checkpoint not found at: {p.resolve()}")

    dev = get_device(device)
    print(f"[INFO] Loading YOLO model: {p.name} on {dev}")
    return YOLO(str(p))


def is_valid_sign_box(
    xyxy: Union[List[int], np.ndarray],
    image_shape: Tuple[int, int],
    confidence: float,
    min_conf: float = 0.60,
    min_area_ratio: float = 0.003,
    max_area_ratio: float = 0.45,
    min_aspect_ratio: float = 0.45,
    max_aspect_ratio: float = 2.2,
) -> bool:
    """
    Geometric false-positive filter. Rejects invalid bounding boxes based on
    aspect ratio, screen area fraction, and confidence thresholds.
    """
    if confidence < min_conf:
        return False

    img_h, img_w = image_shape[:2]
    x1, y1, x2, y2 = xyxy
    box_w = max(0, x2 - x1)
    box_h = max(0, y2 - y1)

    if box_w == 0 or box_h == 0:
        return False

    box_area = box_w * box_h
    total_area = img_w * img_h
    area_ratio = box_area / float(total_area)

    if area_ratio < min_area_ratio or area_ratio > max_area_ratio:
        return False

    aspect_ratio = float(box_w) / float(box_h)
    if aspect_ratio < min_aspect_ratio or aspect_ratio > max_aspect_ratio:
        return False

    return True
