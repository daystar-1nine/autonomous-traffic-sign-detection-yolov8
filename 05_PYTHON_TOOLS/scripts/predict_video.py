"""
Video Inference Pipeline for YOLOv8 Traffic Sign Detection.
Autonomous AI Car Project - 05_PYTHON_TOOLS
"""

import argparse
import sys
import time
from pathlib import Path
import cv2
from ultralytics import YOLO

try:
    from utils import (
        get_device,
        get_project_root,
        load_model,
        draw_detection_box,
        is_valid_sign_box,
        CLASS_NAMES,
    )
except ImportError:
    from .utils import (
        get_device,
        get_project_root,
        load_model,
        draw_detection_box,
        is_valid_sign_box,
        CLASS_NAMES,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run YOLOv8 Traffic Sign Detection on a Video File"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="dataset/demo_traffic_signs.mp4",
        help="Path to input video file (.mp4, .avi, .mov, etc.)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="02_AI_MODEL/weights/best_yolov8n.pt",
        help="Path to trained model weights (default: 02_AI_MODEL/weights/best_yolov8n.pt)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="07_REPORTS/videos/annotated_demo.mp4",
        help="Path to save output video",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.60,
        help="Confidence threshold (default: 0.60 for strict sign filtering)",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.45,
        help="NMS IoU threshold (default: 0.45)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Inference frame size (default: 640)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (e.g., 'cpu', 'cuda:0'). Defaults to auto-detect.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display video frames interactively during processing",
    )
    return parser.parse_args()


def predict_video(args):
    root = get_project_root()
    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = root / source_path

    if not source_path.is_file():
        raise FileNotFoundError(f"Input video file not found at: {source_path}")

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = root / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(source_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {source_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))

    model = load_model(args.model, device=args.device)
    device = get_device(args.device)

    print("\n" + "=" * 65)
    print(" YOLOV8 VIDEO DETECTION PIPELINE")
    print(f" Input Video: {source_path.name}")
    print(f" Resolution: {width}x{height} | FPS: {fps:.1f} | Total Frames: {total_frames}")
    print(f" Output Video: {out_path}")
    print(f" Device: {device} | Conf: {args.conf} | IoU: {args.iou}")
    print("=" * 65 + "\n")

    frame_idx = 0
    t_start = time.time()
    fps_history = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            frame_idx += 1
            t_frame_start = time.time()

            results = model.predict(
                source=frame,
                conf=args.conf,
                iou=args.iou,
                imgsz=args.imgsz,
                device=device,
                verbose=False,
            )

            r = results[0]
            detected_count = 0

            if r.boxes is not None and len(r.boxes) > 0:
                for box in r.boxes:
                    cls_id = int(box.cls.item())
                    conf = float(box.conf.item())
                    xyxy = box.xyxy.tolist()[0]

                    if not is_valid_sign_box(xyxy, frame.shape):
                        continue

                    cls_name = model.names.get(cls_id, CLASS_NAMES.get(cls_id, f"Class {cls_id}"))

                    draw_detection_box(
                        image=frame,
                        xyxy=xyxy,
                        class_id=cls_id,
                        confidence=conf,
                        class_name=cls_name,
                    )
                    detected_count += 1

            frame_time = time.time() - t_frame_start
            cur_fps = 1.0 / max(frame_time, 1e-4)
            fps_history.append(cur_fps)
            if len(fps_history) > 30:
                fps_history.pop(0)
            avg_fps = sum(fps_history) / len(fps_history)

            overlay_text = f"Autonomous CV | FPS: {avg_fps:.1f} | Signs: {detected_count}"
            cv2.rectangle(frame, (10, 10), (380, 45), (0, 0, 0), -1)
            cv2.putText(
                frame,
                overlay_text,
                (18, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

            writer.write(frame)

            if frame_idx % 30 == 0 or frame_idx == total_frames:
                pct = (frame_idx / total_frames * 100) if total_frames > 0 else 0
                print(f"[Frame {frame_idx}/{total_frames} ({pct:.1f}%)] Processing at {avg_fps:.1f} FPS...")

            if args.show:
                cv2.imshow("Autonomous Car - Traffic Sign Video Detection", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord("q"):
                    print("\n[INFO] Playback interrupted by user.")
                    break

    finally:
        cap.release()
        writer.release()
        if args.show:
            cv2.destroyAllWindows()

    total_time = time.time() - t_start
    print("\n" + "=" * 65)
    print(f" VIDEO PROCESSING COMPLETE")
    print(f" Processed {frame_idx} frames in {total_time:.2f} seconds ({frame_idx/max(total_time,1e-3):.1f} FPS)")
    print(f" Annotated video saved to: {out_path}")
    print("=" * 65 + "\n")

    return str(out_path)


def main():
    args = parse_args()
    try:
        predict_video(args)
    except Exception as e:
        print(f"\n[ERROR] Video detection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
