
import cv2
import torch
import os
import time
from ultralytics import YOLO

# ==========================================
# 1. LOAD MODEL
# ==========================================

MODEL_PATH = "runs/train/traffic_signs_rtx5060-3/weights/best.pt"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

model = YOLO(MODEL_PATH)

device = 0 if torch.cuda.is_available() else "cpu"

print("Model loaded successfully!")
print("Device:", torch.cuda.get_device_name(0) if device == 0 else "CPU")
print("Classes:", model.names)

# ==========================================
# 2. OPEN WEBCAM
# ==========================================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Cannot access webcam. Try changing camera index from 0 to 1.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("\nLive detection started!")
print("Press Q to quit.")

# ==========================================
# 3. LIVE DETECTION
# ==========================================

prev_time = time.time()

try:
    while True:

        success, frame = cap.read()

        if not success:
            print("Unable to read webcam frame.")
            break

        # Run YOLO prediction
        results = model.predict(
            source=frame,
            imgsz=640,
            conf=0.10,
            iou=0.45,
            device=device,
            verbose=False
        )

        # Get detection results
        result = results[0]
        annotated_frame = result.plot()

        detection_count = len(result.boxes)

        # Print detected objects
        if detection_count > 0:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                class_name = model.names[class_id]

                print(
                    f"Detected: {class_name} | "
                    f"Confidence: {confidence:.2%}"
                )

        # Calculate FPS
        current_time = time.time()
        fps = 1 / max(current_time - prev_time, 0.001)
        prev_time = current_time

        # Display information
        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Detections: {detection_count}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Show webcam
        cv2.imshow(
            "YOLOv8 Traffic Sign Detection",
            annotated_frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Detection stopped.")
