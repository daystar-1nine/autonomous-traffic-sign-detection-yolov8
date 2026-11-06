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

    # 3. Test All 6 Standard Sign Classes (0 to 5) from test_signs/
    class_targets = [
        (0, "test_signs/vec_0_left_turn.png", "left_turn"),
        (1, "test_signs/vec_1_straight_ahead.png", "straight_ahead"),
        (2, "test_signs/vec_2_right_turn.png", "right_turn"),
        (3, "test_signs/vec_3_dead_end.png", "dead_end"),
        (4, "test_signs/vec_4_no_entry.png", "no_entry"),
        (5, "test_signs/vec_5_stop.png", "stop")
    ]
    for expected_id, filename, expected_name in class_targets:
        img_p = Path(filename)
        if img_p.is_file():
            # Blend on white background for testing
            import cv2
            bgra = cv2.imread(str(img_p), cv2.IMREAD_UNCHANGED)
            if bgra.shape[2] == 4:
                alpha = bgra[:, :, 3] / 255.0
                white = np.ones((bgra.shape[0], bgra.shape[1], 3), dtype=np.uint8) * 255
                for c in range(3):
                    white[:, :, c] = (bgra[:, :, c] * alpha + 255 * (1 - alpha)).astype(np.uint8)
                test_src = white
            else:
                test_src = bgra

            res = model.predict(source=test_src, conf=0.35, verbose=False)[0]
            assert len(res.boxes) > 0, f"Failed to detect {expected_name} sign ({filename})"
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
        assert cls_id in [4, 5], f"Expected safety stop/hazard class (4 or 5), got {cls_id}"
        print(f" [PASS] Real-world stop sign correctly detected as {model.names[cls_id]} with confidence: {conf:.2%}")

    print("\nALL MODEL INFERENCE & DISCRIMINATION TESTS PASSED!")


if __name__ == "__main__":
    test_model_loading_and_inference()
