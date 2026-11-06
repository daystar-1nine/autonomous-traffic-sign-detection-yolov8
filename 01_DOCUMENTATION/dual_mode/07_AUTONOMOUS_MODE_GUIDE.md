# 07 - Autonomous AI Vision Mode Operational Guide

---

## 1. Purpose
This document explains how to activate, supervise, and operate the vehicle in **Autonomous Mode**, where on-device deep learning (YOLOv8n) and the spatial Decision Engine control vehicle movement.

---

## 2. Requirements
- Assembled car with Redmi smartphone mounted on front chassis at 10°–15° upward angle.
- Printed road traffic signs (`stop`, `left_turn`, `right_turn`, `speed_limit_30`, `speed_limit_60`).
- Phone connected to car Wi-Fi (`AutonomousCar_AP`).

---

## 3. Step-by-Step Operating Instructions

### Step 1: Pre-Flight Check
1. Mount the smartphone firmly in the car bracket with the camera facing forward.
2. Ensure camera lens is clean and track is well-lit.
3. Open the Android app. Check top HUD:
   - `FPS: ~28-30`
   - `AI: ~20-30ms`
   - `CAR UDP: <3ms`

### Step 2: Activating Autonomous Mode
1. Press **Button B** on the Ares Pro controller, or tap the cyan **AUTO (B)** button on the screen.
2. The HUD updates to: `[MODE: AUTONOMOUS AI]` (Cyan).
3. The car begins cruising forward at base speed (`PWM: 600–700`).

### Step 3: Sign Response Behaviors
- **STOP Sign Detected:**
  - Car approaches sign, measures bounding box height ratio.
  - Upon reaching `ACTION_ZONE` (Height ratio > 11%), car executes full stop.
  - Holds stop for 3.0 seconds, then resumes cruising forward.
- **LEFT TURN Sign Detected:**
  - Car slows down, executes calibrated differential left turn (850ms), and resumes straight cruise.
- **RIGHT TURN Sign Detected:**
  - Car executes calibrated differential right turn (850ms) and resumes straight cruise.
- **DEAD END / NO ENTRY Sign:**
  - Emergency safety stop triggered; car halts and holds position.

### Step 4: Overriding Autonomous Mode
- At any second, press **Button A** on the controller to seize manual control instantly.
- Press **Button X** to trigger an immediate Emergency Stop.

---

## 4. Expected Output
- Continuous bounding boxes overlaid onto detected signs.
- Autonomous state machine transitions displayed on HUD in real time.
- Gamepad stick inputs ignored while in Autonomous mode.

---

## 5. Verification Checklist
- [ ] Mode button B switches system to `[MODE: AUTONOMOUS AI]`.
- [ ] Car stops automatically at STOP line for 3 seconds.
- [ ] Pressing Button A immediately returns car to Manual control.
- [ ] Pressing Button X stops car instantly.
