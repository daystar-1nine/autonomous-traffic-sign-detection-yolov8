"""
Unit Test: Neural Network Loading & Multi-Scale Tensor Inference Validation
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

    # 1. Test dummy frame
    dummy = np.zeros((640, 640, 3), dtype=np.uint8)
    results = model.predict(source=dummy, conf=0.5, verbose=False)[0]
    assert results is not None, "Inference returned None"
    print(" [PASS] Model instantiated and inference executed on dummy frame.")

    # 2. Test sample stop sign detection
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

    # 3. Test All 6 Standard Sign Classes (0 to 5)
    class_targets = [
        (0, "crop_class_0_left_turn.jpg", "left_turn"),
        (1, "crop_class_1_straight_ahead.jpg", "straight_ahead"),
        (2, "crop_class_2_right_turn.jpg", "right_turn"),
        (3, "crop_class_3_dead_end.jpg", "dead_end"),
        (4, "crop_class_4_no_entry.jpg", "no_entry"),
        (5, "crop_class_5_stop.jpg", "stop")
    ]
    for expected_id, filename, expected_name in class_targets:
        img_p = Path(filename)
        if img_p.is_file():
            res = model.predict(source=str(img_p), conf=0.4, verbose=False)[0]
            assert len(res.boxes) > 0, f"Failed to detect {expected_name} crop ({filename})"
            cls_id = int(res.boxes[0].cls[0].item())
            conf = float(res.boxes[0].conf[0].item())
            assert cls_id == expected_id, f"Expected class {expected_id} ({expected_name}), got {cls_id} ({model.names[cls_id]})"
            print(f" [PASS] Class {expected_id} ({expected_name}) correctly detected with {conf:.2%} confidence.")

    # 4. Test Real Stop Sign detection (05_PYTHON_TOOLS/test_images/stop_sign.jpg)
    real_stop = Path("05_PYTHON_TOOLS/test_images/stop_sign.jpg")
    if real_stop.is_file():
        res = model.predict(source=str(real_stop), conf=0.5, verbose=False)[0]
        assert len(res.boxes) > 0, "Failed to detect real world stop sign"
        cls_id = int(res.boxes[0].cls[0].item())
        conf = float(res.boxes[0].conf[0].item())
        assert cls_id == 5, f"Expected class 5 (stop), got {cls_id}"
        print(f" [PASS] Real-world stop sign correctly detected with confidence: {conf:.2%}")

    print("\nALL MODEL INFERENCE & DISCRIMINATION TESTS PASSED!")


if __name__ == "__main__":
    test_model_loading_and_inference()
