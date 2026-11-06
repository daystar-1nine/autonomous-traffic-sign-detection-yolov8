"""
Unit Test: Neural Network Loading & Tensor Inference Validation
tests/model_tests/test_model_inference.py
"""

import sys
from pathlib import Path
import numpy as np
from ultralytics import YOLO

# Add root, scripts and ai-training/scripts to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir / "scripts"))
sys.path.append(str(root_dir / "ai-training" / "scripts"))
sys.path.append(str(root_dir / "02_AI_MODEL" / "scripts"))

try:
    from utils import is_valid_sign_box, CLASS_NAMES
except ImportError:
    CLASS_NAMES = ["left_turn", "straight_ahead", "right_turn", "dead_end", "no_entry", "stop"]


def test_model_loading_and_inference():
    weights_path = Path("models/weights/best_yolov8n.pt")
    if not weights_path.is_file():
        weights_path = Path("02_AI_MODEL/weights/best_yolov8n.pt")
    assert weights_path.is_file(), f"Model weights not found at {weights_path}"

    model = YOLO(str(weights_path))
    assert model is not None, "Model failed to instantiate"
    assert len(model.names) == 6, f"Expected 6 classes, got {len(model.names)}"

    # Test dummy frame
    dummy = np.zeros((640, 640, 3), dtype=np.uint8)
    results = model.predict(source=dummy, conf=0.5, verbose=False)[0]
    assert results is not None, "Inference returned None"
    print(" [PASS] Model instantiated and inference executed on dummy frame.")

    # Test sample sign detection
    sample_img = Path("dataset/sample_signs/sample_5_stop.jpg")
    if not sample_img.is_file():
        sample_img = Path("05_PYTHON_TOOLS/test_images/stop_sign.jpg")
    if sample_img.is_file():
        res = model.predict(source=str(sample_img), conf=0.5, verbose=False)[0]
        assert len(res.boxes) > 0, "Failed to detect sign on verified sample image"
        cls_id = int(res.boxes[0].cls[0].item())
        conf = float(res.boxes[0].conf[0].item())
        assert cls_id == 5, f"Expected class 5 (stop), got {cls_id}"
        print(f" [PASS] Sample stop sign correctly detected with confidence: {conf:.2%}")

    print("\nALL MODEL TESTS PASSED!")


if __name__ == "__main__":
    test_model_loading_and_inference()
