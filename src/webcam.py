"""
Real-time Camera & Webcam Detection Pipeline for YOLOv8 Traffic Sign Detection.
Supports standard USB webcams, integrated laptop cameras, DirectShow,
and IP/RTSP/HTTP network streams (DroidCam, ESP32-CAM, etc.).
"""

import argparse
import sys
import time
import threading
from pathlib import Path
from typing import Tuple, Optional
import cv2
from ultralytics import YOLO

# Add parent directory to path to allow absolute package imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.utils import (
    get_device,
    get_project_root,
    load_model,
    draw_detection_box,
    is_valid_sign_box,
    CLASS_NAMES,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Real-Time Traffic Sign Detection for Autonomous Car"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/best.pt",
        help="Path to trained model weights (default: models/best.pt)",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Hardware camera device index (0 = default webcam, 1 = external, default: 0)",
    )
    parser.add_argument(
        "--stream-url",
        type=str,
        default=None,
        help="Network stream URL (e.g. RTSP or HTTP: http://192.168.1.100:4747/video)",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.65,
        help="Initial confidence threshold (default: 0.65 for strict sign filtering)",
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
        help="Inference frame resolution (default: 640)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1280,
        help="Camera capture frame width (default: 1280)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=720,
        help="Camera capture frame height (default: 720)",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="auto",
        choices=["auto", "dshow", "any"],
        help="Video capture backend API (default: auto)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (e.g., 'cpu', 'cuda:0'). Defaults to auto-detect.",
    )
    parser.add_argument(
        "--record",
        type=str,
        default=None,
        help="Optional path to record live video stream to MP4 file",
    )
    return parser.parse_args()


class ThreadedStreamCapture:
    """
    Background threaded frame reader that continuously drains OpenCV's internal
    network buffer. Ensures zero-latency real-time video streaming without lag.
    """
    def __init__(self, source_url: str):
        self.cap = cv2.VideoCapture(source_url)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret, self.frame = self.cap.read()
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._drain_loop, daemon=True)
        self.thread.start()

    def _drain_loop(self):
        while self.running:
            ret = self.cap.grab()
            if not ret:
                time.sleep(0.005)
                continue
            ret, frame = self.cap.retrieve()
            if ret and frame is not None:
                with self.lock:
                    self.ret = ret
                    self.frame = frame

    def read(self) -> Tuple[bool, Optional[any]]:
        with self.lock:
            return self.ret, (self.frame.copy() if self.frame is not None else None)

    def isOpened(self) -> bool:
        return self.cap.isOpened()

    def get(self, prop_id):
        return self.cap.get(prop_id)

    def set(self, prop_id, value):
        return self.cap.set(prop_id, value)

    def release(self):
        self.running = False
        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join(timeout=0.4)
        self.cap.release()


def open_camera(args):
    """Safely opens camera capture handle with fallback mechanisms."""
    if args.stream_url:
        print(f"[INFO] Connecting to low-latency network stream: {args.stream_url}")
        stream_cap = ThreadedStreamCapture(args.stream_url)
        if not stream_cap.isOpened():
            raise RuntimeError(f"Failed to connect to network camera stream: {args.stream_url}")
        return stream_cap

    # Direct hardware camera
    api_pref = cv2.CAP_ANY
    if args.backend == "dshow" or (args.backend == "auto" and sys.platform.startswith("win")):
        api_pref = cv2.CAP_DSHOW

    print(f"[INFO] Opening hardware camera device {args.camera_index} (Backend: {api_pref})...")
    cap = cv2.VideoCapture(args.camera_index, api_pref)

    if not cap.isOpened() and api_pref == cv2.CAP_DSHOW:
        print("[WARN] DirectShow backend failed, falling back to CAP_ANY...")
        cap = cv2.VideoCapture(args.camera_index, cv2.CAP_ANY)

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open camera device at index {args.camera_index}.\n"
            f"Suggestions:\n"
            f"  - Verify your webcam or DroidCam client is connected and active.\n"
            f"  - Check if another application (Zoom, Teams) is using the camera.\n"
            f"  - Try a different index: python src/webcam.py --camera-index 1\n"
            f"  - Or use a video stream: python src/webcam.py --stream-url <url>"
        )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    return cap


def run_webcam(args):
    root = get_project_root()
    model = load_model(args.model, device=args.device)
    device = get_device(args.device)

    cap = open_camera(args)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Camera stream active at resolution: {actual_w}x{actual_h}")

    writer = None
    if args.record:
        record_path = Path(args.record)
        if not record_path.is_absolute():
            record_path = root / record_path
        record_path.parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(record_path), fourcc, 30.0, (actual_w, actual_h))
        print(f"[INFO] Recording stream to: {record_path}")

    save_dir = root / "outputs" / "predictions"
    save_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 65)
    print(" AUTONOMOUS CAR - REAL-TIME TRAFFIC SIGN DETECTION ACTIVE")
    print(" Controls:")
    print("   [Q]      : Quit application")
    print("   [S]      : Save snapshot of current detection")
    print("   [+] / [=]: Increase confidence threshold (+0.05)")
    print("   [-] / [_]: Decrease confidence threshold (-0.05)")
    print("=" * 65 + "\n")

    conf_thresh = args.conf
    fps_history = []
    snapshot_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("\n[WARN] Failed to grab frame from camera stream.")
                break

            t_start = time.time()

            results = model.predict(
                source=frame,
                conf=conf_thresh,
                iou=args.iou,
                imgsz=args.imgsz,
                device=device,
                verbose=False,
            )

            latency_ms = (time.time() - t_start) * 1000
            current_fps = 1000.0 / max(latency_ms, 1e-3)
            fps_history.append(current_fps)
            if len(fps_history) > 30:
                fps_history.pop(0)
            avg_fps = sum(fps_history) / len(fps_history)

            r = results[0]
            detected_signs = []

            if r.boxes is not None and len(r.boxes) > 0:
                for box in r.boxes:
                    cls_id = int(box.cls.item())
                    conf = float(box.conf.item())
                    xyxy = box.xyxy.tolist()[0]

                    # Geometric sanity filter (reject non-sign shapes & background noise)
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
                    detected_signs.append((cls_name, conf))

            # Render Heads-Up Display (HUD)
            hud_bg_w = 460
            hud_bg_h = 75
            cv2.rectangle(frame, (10, 10), (10 + hud_bg_w, 10 + hud_bg_h), (20, 20, 20), -1)
            cv2.rectangle(frame, (10, 10), (10 + hud_bg_w, 10 + hud_bg_h), (0, 255, 0), 1)

            cv2.putText(
                frame,
                f"AUTONOMOUS CAR VISION SYSTEM",
                (20, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                1,
                cv2.LINE_AA,
            )

            status_line = f"FPS: {avg_fps:.1f} | Latency: {latency_ms:.0f}ms | Conf: {conf_thresh:.2f}"
            cv2.putText(
                frame,
                status_line,
                (20, 52),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (200, 200, 200),
                1,
                cv2.LINE_AA,
            )

            if detected_signs:
                top_sign, top_conf = max(detected_signs, key=lambda x: x[1])
                sign_str = f"DETECTED: {top_sign.upper()} ({top_conf*100:.1f}%)"
                sign_color = (0, 0, 255) if "stop" in top_sign or "no_entry" in top_sign else (0, 255, 0)
            else:
                sign_str = "DETECTED: None"
                sign_color = (160, 160, 160)

            cv2.putText(
                frame,
                sign_str,
                (20, 72),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                sign_color,
                2,
                cv2.LINE_AA,
            )

            if writer:
                writer.write(frame)

            cv2.imshow("Autonomous Car - YOLOv8 Live Vision", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                print("\n[INFO] Exiting camera stream...")
                break
            elif key == ord("s"):
                snapshot_idx += 1
                snap_path = save_dir / f"snapshot_{int(time.time())}_{snapshot_idx}.jpg"
                cv2.imwrite(str(snap_path), frame)
                print(f"\n[INFO] Snapshot saved to: {snap_path}")
            elif key in (ord("+"), ord("=")):
                conf_thresh = min(0.95, round(conf_thresh + 0.05, 2))
                print(f"\n[INFO] Confidence threshold increased to: {conf_thresh:.2f}")
            elif key in (ord("-"), ord("_")):
                conf_thresh = max(0.05, round(conf_thresh - 0.05, 2))
                print(f"\n[INFO] Confidence threshold decreased to: {conf_thresh:.2f}")

    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        print("[INFO] Camera resources cleanly released.")


def main():
    args = parse_args()
    try:
        run_webcam(args)
    except Exception as e:
        print(f"\n[ERROR] Webcam detection terminated: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
