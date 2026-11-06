# 05 - Controller Calibration & Deadband Configuration Guide

---

## 1. Purpose
This document explains how to calibrate joystick deadbands, eliminate mechanical stick drift, and fine-tune software parameters in the Android application for the Cosmic Byte Ares Pro.

---

## 2. Requirements
- Android application running on Redmi phone.
- Ares Pro controller connected.
- Access to `AresProController.kt` and `DifferentialDriveController.kt`.

---

## 3. Calibration Parameters

### 1. Joystick Deadband Threshold (`deadbandThreshold = 0.10f`)
- **Default:** `0.10f` (10% deadband).
- **Function:** Any stick reading between `-0.10` and `+0.10` is snapped to exact `0.0`.
- **Drift Elimination:** If the car creeps slowly forward or turns without touching the stick, increase threshold to `0.12f` or `0.15f`.

### 2. Input Smoothing Factor (`inputSmoothingAlpha = 0.25f`)
- **Default:** `0.25f`.
- **Function:** Applies exponential filter:  
  `smoothed = smoothed + alpha * (raw - smoothed)`
- **Tuning:**
  - `0.15f`: Ultra-smooth, cinematic acceleration.
  - `0.40f`: Snappy, aggressive racing response.

### 3. Slew Rates (Acceleration & Deceleration)
- **Acceleration Step (`accelSlewRate = 85`):** Progressive ramp prevents TT motor stall currents.
- **Deceleration Step (`decelSlewRate = 180`):** Responsive braking when releasing the stick.

---

## 4. On-Screen Diagnostic Calibration Procedure
1. Launch the Android app and inspect the **Side Diagnostic Telemetry Box**.
2. Leave the left stick untouched:
   - Check `L-Stick: X: 0.00 | Y: 0.00`.
   - If values fluctuate above `0.00`, increase `deadbandThreshold`.
3. Push stick full forward:
   - Verify `L-Stick: Y: -1.00`.
   - Verify `MOTORS: L: 750 | R: 750 PWM` (under NORMAL profile).
4. Push stick full right:
   - Verify `L-Stick: X: 1.00`.
   - Verify `MOTORS: L: 750 | R: -750 PWM` (skid pivot turn).

---

## 5. Expected Output
- Exact `0.00` idle readings on both axes.
- Smooth, progressive ramp up to profile limit without jitter.

---

## 6. Verification Checklist
- [ ] Idle stick reports exactly `X: 0.00 | Y: 0.00`.
- [ ] No motor buzzing or creeping when stick is released.
- [ ] Full deflection reaches ±1.00 on both axes.
