# 12. ANDROID APPLICATION ARCHITECTURE & CODE TOUR
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Package Structure & Architectural Layers

The Android application is organized into modular packages under `com.autonomous.aicontrol`:

```
android-app/app/src/main/java/com/autonomous/aicontrol/
├── MainActivity.kt                  <-- Main activity, CameraX lifecycle, UI orchestration
├── ai/
│   ├── YoloDetector.kt              <-- LiteRT / TFLite / ONNX inference & NMS pipeline
│   └── DetectionResult.kt           <-- Data class for bounding boxes & class labels
├── controller/
│   ├── AresProController.kt         <-- Bluetooth HID input listener & deadband filter
│   ├── DifferentialDriveController.kt<-- Slew-rate limiter & differential steering math
│   ├── ControlModeManager.kt        <-- State machine arbitration (MANUAL / AUTO / STOP)
│   └── GamepadDiagnosticData.kt     <-- Telemetry data class for HUD overlay
├── decision/
│   └── DecisionEngine.kt            <-- Temporal persistence filter & car action triggers
├── network/
│   └── UdpVehicleClient.kt          <-- High-frequency, non-blocking UDP socket
└── ui/
    └── OverlayView.kt               <-- Real-time hardware-accelerated bounding box renderer
```

---

## 2. Core Subsystems Deep Dive

### 2.1 CameraX Non-Blocking Image Analysis Pipeline
In `MainActivity.kt`, CameraX is configured with `STRATEGY_KEEP_ONLY_LATEST`:
```kotlin
val imageAnalysis = ImageAnalysis.Builder()
    .setTargetResolution(Size(640, 640))
    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
    .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
    .build()
```
- **Zero Latency Backlog:** If inference takes 15 ms, the camera pipeline automatically discards older frames rather than queuing them. The neural detector always receives the absolute freshest frame.

### 2.2 AresProController & Input Handling
Captures analog thumbstick motions and button presses:
- **Deadband Filter:** Rejects thumbstick center drift $<0.10$ normalized deflection to prevent phantom creeps.
- **Trigger Normalization:** Hall-effect magnetic triggers (LT/RT) are normalized from $[0.0, 1.0]$.
- **Hardware Profile Switching:** Pressing **Y** cycles through `ECO` (500 max PWM), `NORMAL` (750 max PWM), and `SPORT` (1000 max PWM).

### 2.3 DifferentialDriveController
Implements smooth vehicular acceleration and deceleration:
- **Acceleration Slew Rate (85 PWM/tick):** Prevents sudden motor jerk, wheel slip, and battery voltage sag.
- **Deceleration Slew Rate (180 PWM/tick):** Provides snappy, responsive braking when thumbstick is released.
- **Skid-Steer Pivot Turning:** Allows in-place 360-degree rotation when throttle is zero and steering is deflected.

### 2.4 ControlModeManager & Safety Priority
- States: `MANUAL`, `AUTONOMOUS`, `EMERGENCY_STOP`.
- **Preemption Rule:** `EMERGENCY_STOP` has absolute priority. It immediately zeroes motor PWM, locks the control pipeline, and requires explicit user unlock.
- **Controller Disconnection Failsafe:** If the Ares Pro gamepad disconnects while in `MANUAL` mode, the vehicle immediately stops and enters failsafe halt.
