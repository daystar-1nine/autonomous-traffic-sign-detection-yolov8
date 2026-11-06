"""
Camera Diagnostic & Stream Verification Tool
Autonomous AI Car Project
Tests webcams, phone RTSP/HTTP streams, and diagnoses privacy shutters.
"""

import argparse
import time
import cv2


def parse_args():
    parser = argparse.ArgumentParser(description="Test Camera Capture & Latency")
    parser.add_argument("--index", type=int, default=0, help="Hardware camera index")
    parser.add_argument("--stream-url", type=str, default=None, help="Network stream URL")
    parser.add_argument("--width", type=int, default=1280, help="Frame width")
    parser.add_argument("--height", type=int, default=720, help="Frame height")
    return parser.parse_args()


def main():
    args = parse_args()
    source = args.stream_url if args.stream_url else args.index

    print(f"\n[INFO] Opening camera source: {source}...")
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[FAIL] Could not open camera source: {source}")
        print("Tip: If physical webcam is closed, open the hardware privacy slider.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    print("[SUCCESS] Camera stream opened! Press 'Q' to exit.")
    prev_t = time.time()
    frames = 0

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[WARN] Failed to read frame.")
            break

        frames += 1
        now = time.time()
        fps = 1.0 / max(1e-4, now - prev_t)
        prev_t = now

        cv2.putText(frame, f"CAMERA TEST | FPS: {fps:.1f}", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Camera Diagnostic Tool", frame)

        if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q'), 27):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[CLOSED] Stream closed cleanly after {frames} frames.\n")


if __name__ == "__main__":
    main()
