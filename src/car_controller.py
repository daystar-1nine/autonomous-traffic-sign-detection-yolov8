"""
==============================================================================
AI-Based Autonomous Car: Real-Time Vision Brain & Vehicle Controller
==============================================================================
Ties together:
1. Low-latency phone camera stream (DroidCam / RTSP / HTTP MJPEG)
2. YOLOv8s Deep Learning Object Detection (NVIDIA RTX GPU accelerated)
3. Spatial Sign Proximity Analysis & Geometric False-Positive Filtering
4. Temporal State Machine (Cruise, Turn, Stop & Hold, Speed Limit)
5. Asynchronous Non-blocking HTTP Telemetry to NodeMCU ESP8266 + TB6612FNG
6. Full Autonomous Cockpit HUD with Manual Keyboard Override (WASD)
==============================================================================
"""

import argparse
import sys
import time
import math
import queue
import threading
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import requests
import cv2
import numpy as np
from ultralytics import YOLO

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.utils import (
    get_device,
    get_project_root,
    load_model,
    is_valid_sign_box,
    CLASS_NAMES,
    CLASS_COLORS,
)


class AsyncCarClient:
    """
    Non-blocking HTTP client for NodeMCU ESP8266.
    Sends navigation commands via a background worker thread so the
    OpenCV video display and YOLO inference never stutter or lag.
    """
    def __init__(self, esp_ip: str, port: int = 80):
        self.esp_ip = esp_ip
        self.port = port
        self.base_url = f"http://{esp_ip}:{port}"
        self.command_queue: queue.Queue = queue.Queue(maxsize=3)
        self.last_sent_command: str = "STOP"
        self.last_ping_ms: float = -1.0
        self.is_connected: bool = False
        self._running: bool = True

        # Start background worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def send(self, cmd: str, speed: Optional[int] = None):
        """Queue a command for non-blocking transmission."""
        if not self._running:
            return
        # Drop older queued commands if queue is full to ensure only latest state is sent
        try:
            while not self.command_queue.empty():
                self.command_queue.get_nowait()
        except queue.Empty:
            pass
        self.command_queue.put((cmd, speed))

    def _worker_loop(self):
        """Worker thread executing HTTP requests."""
        session = requests.Session()
        while self._running:
            try:
                cmd, speed = self.command_queue.get(timeout=0.2)
                url = f"{self.base_url}/car?cmd={cmd}"
                if speed is not None:
                    url += f"&speed={speed}"

                t0 = time.time()
                resp = session.get(url, timeout=0.35)
                dt = (time.time() - t0) * 1000.0

                if resp.status_code == 200:
                    self.last_sent_command = cmd
                    self.last_ping_ms = round(dt, 1)
                    self.is_connected = True
                else:
                    self.is_connected = False
            except queue.Empty:
                # Periodic ping if idle to monitor connection health
                if time.time() % 3.0 < 0.2:
                    try:
                        t0 = time.time()
                        r = session.get(f"{self.base_url}/ping", timeout=0.25)
                        self.last_ping_ms = round((time.time() - t0) * 1000.0, 1)
                        self.is_connected = (r.status_code == 200)
                    except Exception:
                        self.is_connected = False
                        self.last_ping_ms = -1.0
            except Exception:
                self.is_connected = False
                self.last_ping_ms = -1.0

    def close(self):
        self._running = False
        # Send emergency stop before exiting
        try:
            requests.get(f"{self.base_url}/car?cmd=STOP", timeout=0.3)
        except Exception:
            pass


class ThreadedStreamCapture:
    """
    Zero-latency background frame reader that continuously flushes OpenCV's
    internal network buffer, ensuring 100% real-time camera frames.
    """
    def __init__(self, source_url: str):
        self.cap = cv2.VideoCapture(source_url)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret, self.frame = self.cap.read()
        self.running = True
        self.lock = threading.Lock()

        if not self.ret or self.frame is None:
            raise RuntimeError(f"Failed to connect to camera stream at: {source_url}")

        self.thread = threading.Thread(target=self._capture_worker, daemon=True)
        self.thread.start()

    def _capture_worker(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self.lock:
                    self.ret = ret
                    self.frame = frame
            else:
                time.sleep(0.01)

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        with self.lock:
            return self.ret, self.frame.copy() if self.frame is not None else None

    def release(self):
        self.running = False
        if self.cap:
            self.cap.release()


class AutonomousVehicleController:
    """
    Core Autonomous Driving Brain.
    Translates computer vision detections into safe, debounced,
    distance-aware vehicle maneuvers.
    """
    def __init__(
        self,
        model_path: str,
        esp_ip: str,
        stream_url: str,
        device: Optional[str] = None,
        conf_thresh: float = 0.65,
        cruise_speed: int = 700,
        turn_speed: int = 750,
        turn_duration_sec: float = 0.85,
        stop_hold_sec: float = 3.0,
    ):
        self.conf_thresh = conf_thresh
        self.cruise_speed = cruise_speed
        self.turn_speed = turn_speed
        self.turn_duration_sec = turn_duration_sec
        self.stop_hold_sec = stop_hold_sec

        # Load AI Model
        self.device = get_device(device)
        self.model = load_model(model_path, device=self.device)

        # Network Client & Camera
        self.car = AsyncCarClient(esp_ip)
        self.camera = ThreadedStreamCapture(stream_url)

        # State Machine States: CRUISING, TURNING, STOPPED, COOLDOWN, MANUAL
        self.state = "CRUISING"
        self.state_start_time = time.time()
        self.last_action_sign: Optional[str] = None
        self.cooldown_until: float = 0.0

        # Detection Continuity Debouncing
        self.detection_history: Dict[str, int] = {}
        self.MIN_CONSECUTIVE_FRAMES = 2

        # Manual Override Flag
        self.manual_override = False

        # Telemetry History
        self.fps_history = []
        self.last_frame_time = time.time()

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Runs YOLOv8 detection, updates navigation state machine,
        and returns annotated frame with telemetry data.
        """
        h, w = frame.shape[:2]
        t0 = time.time()

        # Run YOLO inference
        results = self.model.predict(
            source=frame,
            conf=self.conf_thresh,
            iou=0.45,
            device=self.device,
            verbose=False,
            imgsz=640,
        )[0]
        inference_ms = (time.time() - t0) * 1000.0

        # Filter valid signs using geometric & aspect-ratio filter
        valid_detections = []
        if results.boxes is not None and len(results.boxes) > 0:
            for box in results.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].cpu().numpy().astype(int)

                if is_valid_sign_box(xyxy, (h, w), conf, min_conf=self.conf_thresh):
                    box_w = xyxy[2] - xyxy[0]
                    box_h = xyxy[3] - xyxy[1]
                    area_ratio = (box_w * box_h) / (w * h)
                    height_ratio = box_h / h

                    valid_detections.append({
                        "cls_id": cls_id,
                        "name": CLASS_NAMES.get(cls_id, f"sign_{cls_id}"),
                        "conf": conf,
                        "box": xyxy,
                        "area_ratio": area_ratio,
                        "height_ratio": height_ratio,
                    })

        # Sort detections by proximity (largest area = closest to car)
        valid_detections.sort(key=lambda d: d["area_ratio"], reverse=True)
        primary_detection = valid_detections[0] if valid_detections else None

        # Update Navigation State Machine
        telemetry = self._update_navigation(primary_detection, h, w)
        telemetry["inference_ms"] = inference_ms
        telemetry["detections_count"] = len(valid_detections)

        # Draw Futuristic Autonomous Cockpit HUD
        annotated = self._render_cockpit_hud(frame, valid_detections, telemetry)
        return annotated, telemetry

    def _update_navigation(self, sign: Optional[Dict[str, Any]], frame_h: int, frame_w: int) -> Dict[str, Any]:
        """
        Autonomous Decision & State Machine:
        Controls the car based on sign proximity, confidence, and cooldown timers.
        """
        now = time.time()
        dt_state = now - self.state_start_time

        telemetry: Dict[str, Any] = {
            "state": self.state,
            "target_sign": "None",
            "proximity_pct": 0.0,
            "target_distance": "CLEAR",
            "action": "CRUISING",
            "speed": self.cruise_speed,
        }

        # If in Manual Override mode, skip AI decision logic
        if self.manual_override:
            telemetry["state"] = "MANUAL"
            telemetry["action"] = self.car.last_sent_command
            return telemetry

        # Update debounce tracking
        current_seen_name = sign["name"] if sign else None
        for name in list(self.detection_history.keys()):
            if name != current_seen_name:
                self.detection_history[name] = max(0, self.detection_history[name] - 1)
        if current_seen_name:
            self.detection_history[current_seen_name] = self.detection_history.get(current_seen_name, 0) + 1

        # Check if sign is debounced (confirmed for N consecutive frames)
        is_debounced = (
            sign is not None and
            self.detection_history.get(sign["name"], 0) >= self.MIN_CONSECUTIVE_FRAMES
        )

        # Calculate Sign Proximity Metric (Estimated Distance)
        proximity_pct = 0.0
        if sign:
            # Box height ratio: > 14% = Action Zone (~0.5m), < 6% = Far Approach (>1.5m)
            proximity_pct = min(100.0, (sign["height_ratio"] / 0.22) * 100.0)
            telemetry["target_sign"] = sign["name"]
            telemetry["proximity_pct"] = round(proximity_pct, 1)

            if sign["height_ratio"] > 0.12:
                telemetry["target_distance"] = "ACTION_ZONE"
            elif sign["height_ratio"] > 0.06:
                telemetry["target_distance"] = "APPROACHING"
            else:
                telemetry["target_distance"] = "FAR"

        # ---------------- STATE MACHINE TRANSITIONS ----------------
        if self.state == "TURNING":
            # Continue turning until calibrated duration completes
            if dt_state >= self.turn_duration_sec:
                # Turn completed! Return to cruising with cooldown
                self.state = "CRUISING"
                self.cooldown_until = now + 2.5 # 2.5s cooldown against duplicate turns
                self.car.send("FORWARD", self.cruise_speed)
                self.state_start_time = now
            else:
                telemetry["action"] = self.last_action_sign
                return telemetry

        elif self.state == "STOPPED":
            # Hold at regulatory stop line for stop_hold_sec
            if dt_state >= self.stop_hold_sec:
                # Stop holding period expired -> safely resume forward motion
                self.state = "CRUISING"
                self.cooldown_until = now + 3.0 # Cooldown so car doesn't re-stop immediately
                self.car.send("FORWARD", self.cruise_speed)
                self.state_start_time = now
            else:
                telemetry["action"] = f"HOLDING STOP ({round(self.stop_hold_sec - dt_state, 1)}s)"
                self.car.send("STOP")
                return telemetry

        elif self.state == "CRUISING":
            # Check if we are in cooldown from a recent maneuver
            in_cooldown = (now < self.cooldown_until)

            if is_debounced and not in_cooldown:
                sign_name = sign["name"]
                h_ratio = sign["height_ratio"]

                # 1. STOP SIGN
                if sign_name == "stop":
                    if h_ratio > 0.10: # Reached stop threshold
                        self.state = "STOPPED"
                        self.state_start_time = now
                        self.last_action_sign = "STOP"
                        self.car.send("STOP")
                        telemetry["action"] = "STOPPING"
                        return telemetry
                    else:
                        # Approaching stop sign: slow down smoothly
                        self.car.send("SLOW", 480)
                        telemetry["action"] = "DECELERATING (STOP AHEAD)"
                        return telemetry

                # 2. NO ENTRY / DEAD END
                elif sign_name in ("no_entry", "dead_end"):
                    if h_ratio > 0.10:
                        self.state = "STOPPED"
                        self.state_start_time = now
                        self.last_action_sign = "BLOCKED"
                        self.car.send("STOP")
                        telemetry["action"] = f"EMERGENCY BRAKE ({sign_name.upper()})"
                        return telemetry

                # 3. LEFT TURN
                elif sign_name == "left_turn":
                    if h_ratio > 0.11: # In turning zone!
                        self.state = "TURNING"
                        self.state_start_time = now
                        self.last_action_sign = "LEFT"
                        self.car.send("LEFT", self.turn_speed)
                        telemetry["action"] = "EXECUTING LEFT TURN"
                        return telemetry
                    else:
                        # Slow down in preparation for turn
                        self.car.send("FORWARD", 520)
                        telemetry["action"] = "PREPARING LEFT TURN"
                        return telemetry

                # 4. RIGHT TURN
                elif sign_name == "right_turn":
                    if h_ratio > 0.11: # In turning zone!
                        self.state = "TURNING"
                        self.state_start_time = now
                        self.last_action_sign = "RIGHT"
                        self.car.send("RIGHT", self.turn_speed)
                        telemetry["action"] = "EXECUTING RIGHT TURN"
                        return telemetry
                    else:
                        # Slow down in preparation for turn
                        self.car.send("FORWARD", 520)
                        telemetry["action"] = "PREPARING RIGHT TURN"
                        return telemetry

                # 5. STRAIGHT AHEAD
                elif sign_name == "straight_ahead":
                    self.car.send("FORWARD", self.cruise_speed)
                    telemetry["action"] = "CRUISING (CLEAR PATH)"
                    return telemetry

            # Default: Maintain normal cruise
            self.car.send("FORWARD", self.cruise_speed)
            telemetry["action"] = "CRUISING FORWARD"

        return telemetry

    def _render_cockpit_hud(
        self,
        frame: np.ndarray,
        detections: list,
        telemetry: Dict[str, Any],
    ) -> np.ndarray:
        """
        Draws high-tech autonomous cockpit telemetry overlay.
        """
        hud = frame.copy()
        h, w = hud.shape[:2]

        # Draw detected bounding boxes
        for det in detections:
            xyxy = det["box"]
            cls_id = det["cls_id"]
            name = det["name"].upper().replace("_", " ")
            conf = det["conf"]
            color = CLASS_COLORS.get(cls_id, (0, 255, 0))

            # Bounding box
            cv2.rectangle(hud, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), color, 3)

            # High-visibility badge
            label = f"{name} {int(conf * 100)}%"
            font = cv2.FONT_HERSHEY_DUPLEX
            (tw, th), _ = cv2.getTextSize(label, font, 0.65, 2)
            cv2.rectangle(
                hud,
                (xyxy[0], max(0, xyxy[1] - th - 12)),
                (xyxy[0] + tw + 12, max(th + 12, xyxy[1])),
                color,
                -1,
            )
            cv2.putText(
                hud,
                label,
                (xyxy[0] + 6, max(th + 6, xyxy[1] - 6)),
                font,
                0.65,
                (0, 0, 0),
                2,
                cv2.LINE_AA,
            )

        # ---------------- TOP TELEMETRY BANNER ----------------
        overlay = hud.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (15, 20, 25), -1)
        cv2.addWeighted(overlay, 0.85, hud, 0.15, 0, hud)

        # Header Title
        cv2.putText(
            hud,
            "AUTONOMOUS ROBOTIC VEHICLE | AI VISION ENGINE",
            (20, 28),
            cv2.FONT_HERSHEY_DUPLEX,
            0.65,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Mode Badge (Auto / Manual)
        mode_color = (0, 255, 0) if not self.manual_override else (0, 165, 255)
        mode_text = "AUTO [AI ACTIVE]" if not self.manual_override else "MANUAL [OVERRIDE]"
        cv2.rectangle(hud, (w - 240, 12), (w - 20, 42), mode_color, 2)
        cv2.putText(
            hud,
            mode_text,
            (w - 230, 34),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            mode_color,
            2,
            cv2.LINE_AA,
        )

        # Sub-status: FPS, GPU Latency, Car WiFi Latency
        now = time.time()
        fps = 1.0 / max(1e-4, (now - self.last_frame_time))
        self.last_frame_time = now
        self.fps_history.append(fps)
        if len(self.fps_history) > 30:
            self.fps_history.pop(0)
        avg_fps = sum(self.fps_history) / len(self.fps_history)

        ping_str = f"{self.car.last_ping_ms}ms" if self.car.is_connected else "DISCONNECTED"
        ping_color = (0, 255, 0) if self.car.is_connected else (0, 0, 255)

        stats_line = (
            f"FPS: {avg_fps:.1f} | GPU Latency: {telemetry.get('inference_ms', 0):.1f}ms | "
            f"Car WiFi: "
        )
        cv2.putText(
            hud,
            stats_line,
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (200, 200, 200),
            1,
            cv2.LINE_AA,
        )
        (sl_w, _), _ = cv2.getTextSize(stats_line, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
        cv2.putText(
            hud,
            ping_str,
            (20 + sl_w, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            ping_color,
            2,
            cv2.LINE_AA,
        )

        # ---------------- BOTTOM NAVIGATION HUD ----------------
        bottom_h = 100
        overlay_b = hud.copy()
        cv2.rectangle(overlay_b, (0, h - bottom_h), (w, h), (15, 20, 25), -1)
        cv2.addWeighted(overlay_b, 0.88, hud, 0.12, 0, hud)

        # Action / Command Box
        action_text = telemetry.get("action", "CRUISING")
        action_color = (0, 255, 0)
        if "STOP" in action_text or "BRAKE" in action_text:
            action_color = (0, 0, 255)
        elif "LEFT" in action_text or "RIGHT" in action_text:
            action_color = (0, 215, 255)

        cv2.putText(
            hud,
            f"VEHICLE ACTION: {action_text}",
            (25, h - 60),
            cv2.FONT_HERSHEY_DUPLEX,
            0.8,
            action_color,
            2,
            cv2.LINE_AA,
        )

        # Target Sign & Proximity Bar
        target_sign = telemetry.get("target_sign", "None").upper().replace("_", " ")
        proximity = telemetry.get("proximity_pct", 0.0)
        cv2.putText(
            hud,
            f"TARGET SIGN: {target_sign} | DISTANCE ZONE: {telemetry.get('target_distance', 'CLEAR')}",
            (25, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )

        # Proximity Progress Bar on Right Side
        bar_x = w - 240
        bar_y = h - 55
        bar_w = 200
        bar_h = 18
        cv2.rectangle(hud, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (80, 80, 80), 1)
        fill_w = int((proximity / 100.0) * bar_w)
        fill_color = (0, 255, 0) if proximity < 50 else (0, 165, 255) if proximity < 80 else (0, 0, 255)
        if fill_w > 0:
            cv2.rectangle(hud, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), fill_color, -1)
        cv2.putText(
            hud,
            f"PROXIMITY: {int(proximity)}%",
            (bar_x, bar_y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (200, 200, 200),
            1,
            cv2.LINE_AA,
        )

        return hud

    def run(self):
        """Main real-time autonomous loop with interactive keyboard controls."""
        print("\n=======================================================")
        print("  AI AUTONOMOUS CAR VISION SYSTEM INITIALIZED          ")
        print("=======================================================")
        print(" Controls:")
        print("  [M]        : Toggle Autonomous / Manual Mode")
        print("  [SPACE]    : Emergency Stop")
        print("  [W,A,S,D]  : Manual Steering (when in Manual mode)")
        print("  [+ / -]    : Adjust Confidence Threshold (+/- 0.05)")
        print("  [Q / ESC]  : Safely Exit")
        print("=======================================================\n")

        cv2.namedWindow("Autonomous Car Cockpit HUD", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Autonomous Car Cockpit HUD", 1280, 720)

        try:
            while True:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    time.sleep(0.01)
                    continue

                # Process frame through autonomous pipeline
                annotated_frame, telemetry = self.process_frame(frame)

                cv2.imshow("Autonomous Car Cockpit HUD", annotated_frame)
                key = cv2.waitKey(1) & 0xFF

                if key in (ord('q'), ord('Q'), 27): # ESC or Q
                    print("\n[INFO] Exiting vehicle controller...")
                    break

                elif key in (ord('m'), ord('M')):
                    self.manual_override = not self.manual_override
                    mode_name = "MANUAL" if self.manual_override else "AUTONOMOUS"
                    print(f"\n[MODE CHANGE] Switched to {mode_name} mode!")
                    if self.manual_override:
                        self.car.send("STOP")

                elif key == 32: # SPACE = Emergency Stop
                    print("\n[ALERT] EMERGENCY STOP TRIGGERED!")
                    self.manual_override = True
                    self.car.send("STOP")

                elif self.manual_override:
                    # Manual driving keys
                    if key in (ord('w'), ord('W')):
                        self.car.send("FORWARD", self.cruise_speed)
                    elif key in (ord('s'), ord('S')):
                        self.car.send("BACKWARD", self.cruise_speed)
                    elif key in (ord('a'), ord('A')):
                        self.car.send("LEFT", self.turn_speed)
                    elif key in (ord('d'), ord('D')):
                        self.car.send("RIGHT", self.turn_speed)

                # Confidence adjustment
                if key in (ord('+'), ord('=')):
                    self.conf_thresh = min(0.95, self.conf_thresh + 0.05)
                    print(f"[CONFIG] Confidence threshold raised to: {self.conf_thresh:.2f}")
                elif key in (ord('-'), ord('_')):
                    self.conf_thresh = max(0.20, self.conf_thresh - 0.05)
                    print(f"[CONFIG] Confidence threshold lowered to: {self.conf_thresh:.2f}")

        finally:
            print("[INFO] Shutting down car and camera stream...")
            self.car.send("STOP")
            self.car.close()
            self.camera.release()
            cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Car Real-Time AI Controller"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/best.pt",
        help="Path to YOLOv8 model weights (default: models/best.pt)",
    )
    parser.add_argument(
        "--esp-ip",
        type=str,
        default="192.168.4.1",
        help="IP Address of ESP8266 (default: 192.168.4.1 for Car AP mode)",
    )
    parser.add_argument(
        "--stream-url",
        type=str,
        required=True,
        help="Phone Camera stream URL (e.g. 'http://192.168.137.1:4747/video')",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.65,
        help="Sign detection confidence threshold (default: 0.65)",
    )
    parser.add_argument(
        "--cruise-speed",
        type=int,
        default=700,
        help="Standard forward cruise speed 0-1023 (default: 700)",
    )
    parser.add_argument(
        "--turn-speed",
        type=int,
        default=750,
        help="Turning maneuver speed 0-1023 (default: 750)",
    )
    parser.add_argument(
        "--turn-duration",
        type=float,
        default=0.85,
        help="Duration of turn in seconds (default: 0.85s)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (e.g. 'cuda:0', 'cpu')",
    )

    args = parser.parse_args()

    controller = AutonomousVehicleController(
        model_path=args.model,
        esp_ip=args.esp_ip,
        stream_url=args.stream_url,
        device=args.device,
        conf_thresh=args.conf,
        cruise_speed=args.cruise_speed,
        turn_speed=args.turn_speed,
        turn_duration_sec=args.turn_duration,
    )
    controller.run()


if __name__ == "__main__":
    main()
