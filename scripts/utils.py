"""
Utility functions and configuration for YOLOv8 Traffic Sign Detection.
Autonomous AI Car Project - 05_PYTHON_TOOLS
"""

import os
import json
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Union
import cv2
import numpy as np
import torch
from ultralytics import YOLO

# Standard 6 traffic sign classes
CLASS_NAMES: Dict[int, str] = {
    0: "left_turn",
    1: "straight_ahead",
    2: "right_turn",
    3: "dead_end",
    4: "no_entry",
    5: "stop",
}

# Distinct BGR color palette for visualization in autonomous driving
CLASS_COLORS: Dict[int, Tuple[int, int, int]] = {
    0: (255, 128, 0),    # Left Turn: Sky Blue / Cyan
    1: (0, 200, 0),      # Straight Ahead: Bright Green
    2: (0, 165, 255),    # Right Turn: Orange
    3: (0, 215, 255),    # Dead End: Yellow
    4: (0, 69, 255),     # No Entry: Orange-Red
    5: (0, 0, 255),      # Stop: Deep Red
}


def get_project_root() -> Path:
    """Returns the absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def get_device(preferred_device: Optional[str] = None) -> str:
    """
    Selects the optimal execution device.
    Falls back gracefully to CPU if CUDA is requested but unavailable.
    """
    if preferred_device:
        device_lower = str(preferred_device).lower().strip()
        if "cuda" in device_lower or device_lower in ("0", "1", "2"):
            if torch.cuda.is_available():
                return preferred_device
            print("[WARN] CUDA requested but not available. Falling back to CPU.")
            return "cpu"
        return preferred_device

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"[INFO] CUDA GPU detected: {gpu_name}")
        return "cuda:0"

    print("[INFO] CUDA GPU not detected. Using CPU device.")
    return "cpu"


def load_model(model_path: Union[str, Path] = "02_AI_MODEL/weights/best_yolov8n.pt", device: Optional[str] = None) -> YOLO:
    """
    Loads a YOLO model from file path with verification.
    """
    model_path = Path(model_path)
    if not model_path.is_absolute():
        model_path = get_project_root() / model_path

    if not model_path.is_file():
        raise FileNotFoundError(
            f"Model weights not found at: {model_path}\n"
            f"Please ensure weights exist under 02_AI_MODEL/weights/ or provide a valid path."
        )

    device_str = get_device(device)
    print(f"[INFO] Loading YOLO model from: {model_path.name} on {device_str}")
    model = YOLO(str(model_path))
    return model


def is_valid_sign_box(
    xyxy: Union[List[float], np.ndarray],
    image_shape: Tuple[int, int],
    confidence: float = 1.0,
    min_conf: float = 0.50,
    min_area_ratio: float = 0.003,
    max_area_ratio: float = 0.45,
    min_aspect_ratio: float = 0.45,
    max_aspect_ratio: float = 2.2,
) -> bool:
    """
    Validates whether a bounding box matches the geometric properties of a traffic sign.
    Rejects room clutter, walls, furniture, door frames, and random background noise.
    """
    if confidence < min_conf:
        return False

    h_img, w_img = image_shape[:2]
    img_area = max(1, h_img * w_img)
    x1, y1, x2, y2 = xyxy
    box_w = max(0.0, x2 - x1)
    box_h = max(0.0, y2 - y1)
    if box_w <= 4 or box_h <= 4:
        return False

    box_area = box_w * box_h
    area_ratio = box_area / img_area
    if area_ratio < min_area_ratio or area_ratio > max_area_ratio:
        return False

    aspect_ratio = box_w / box_h
    if aspect_ratio < min_aspect_ratio or aspect_ratio > max_aspect_ratio:
        return False

    return True


def draw_detection_box(
    image: np.ndarray,
    xyxy: List[float],
    class_id: int,
    confidence: float,
    class_name: Optional[str] = None,
    color: Optional[Tuple[int, int, int]] = None,
    line_thickness: int = 2,
    font_scale: float = 0.55,
) -> np.ndarray:
    """
    Draws a styled, anti-aliased bounding box with filled badge background.
    """
    x1, y1, x2, y2 = [int(round(coord)) for coord in xyxy]
    h, w = image.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w - 1, x2), min(h - 1, y2)

    if color is None:
        color = CLASS_COLORS.get(class_id, (0, 255, 0))

    name = class_name or CLASS_NAMES.get(class_id, f"Class {class_id}")
    label_text = f"{name} {confidence * 100:.1f}%"

    # Draw primary bounding rectangle
    cv2.rectangle(image, (x1, y1), (x2, y2), color, line_thickness, cv2.LINE_AA)

    # Calculate text badge size
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, 1)

    badge_y1 = max(0, y1 - text_h - baseline - 6)
    badge_y2 = y1
    badge_x2 = min(w - 1, x1 + text_w + 8)

    # If badge would clip top of image, place it inside bounding box
    if badge_y1 == 0 and y1 < text_h + 10:
        badge_y1 = y1
        badge_y2 = y1 + text_h + baseline + 6

    # Draw badge background
    cv2.rectangle(image, (x1, badge_y1), (badge_x2, badge_y2), color, -1)

    # Draw contrasting text
    luminance = 0.299 * color[2] + 0.587 * color[1] + 0.114 * color[0]
    text_color = (0, 0, 0) if luminance > 160 else (255, 255, 255)

    cv2.putText(
        image,
        label_text,
        (x1 + 4, badge_y2 - baseline - 2),
        font,
        font_scale,
        text_color,
        1,
        cv2.LINE_AA,
    )

    return image


def save_detection_summary(
    results_list: List[Dict],
    output_path: Union[str, Path]
) -> None:
    """
    Saves detection summary metadata to a formatted JSON file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_list, f, indent=2)
    print(f"[INFO] Detection summary saved to: {output_path}")
