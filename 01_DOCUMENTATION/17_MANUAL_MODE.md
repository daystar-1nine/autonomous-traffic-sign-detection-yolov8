# 17 - Manual Control Mode & Emergency Brake

This document explains the **Manual Override Mode** and **Emergency Brake** safety mechanisms implemented in the Android application and Python desktop suite.

---

## 🎮 Purpose of Manual Mode

Autonomous vehicles must always feature a hardware-independent manual override mechanism for:
1. Driving the car to the starting line of a test track without picking it up.
2. Calibrating straight-line motor trim on different surfaces (tiles, wood, carpet).
3. Safely regaining control if an unexpected physical obstacle appears.

---

## 📱 Activating Manual Mode on the Android App

1. In the bottom control bar of the Android app, tap the **MODE: AUTO** button.
2. The button will toggle to cyan: **MODE: MANUAL**.
3. In Manual Mode:
   - AI detections still render on the HUD with bounding boxes.
   - The Decision Engine ceases issuing autonomous steering and stopping commands.
   - The vehicle stops and awaits explicit manual input.

---

## 🛑 Emergency Brake Button

The red **EMERGENCY STOP** button is permanently anchored to the bottom-right corner of the Android HUD screen:
- **Instant Actuation:** Tapping the button immediately transmits three consecutive `CMD:STOP:0:0\n` UDP packets.
- **Safety Lockout:** Forces the vehicle into `EMERGENCY_STOP` state and locks motor PWM at `0`.
- **Reset:** To resume driving after an emergency stop, toggle the mode button back to **AUTO MODE**.

---

## 💻 Desktop Simulation Controls (When using PC Telemetry HUD)

When running [`05_PYTHON_TOOLS/scripts/pc_telemetry_hud.py`](../05_PYTHON_TOOLS/scripts/pc_telemetry_hud.py) on a laptop:

| Key | Action |
| :---: | :--- |
| **`M`** | Toggle Autonomous Mode $\leftrightarrow$ Manual Mode |
| **`SPACE`** | **Emergency Zero-Speed Brake** |
| **`W`** | Drive Forward |
| **`S`** | Reverse |
| **`A`** | Steer Left |
| **`D`** | Steer Right |
| **`1`** | Set Speed to Low / Speed Limit (PWM 450) |
| **`2`** | Set Speed to Cruise (PWM 700) |
| **`3`** | Set Speed to Turbo (PWM 920) |
| **`[` / `]`** | Adjust Motor Trim (-5 / +5) |
| **`T`** | Run 90° Turn Calibration Test |

---

👉 **Next Step:** Proceed to [`18_MOTOR_CALIBRATION.md`](18_MOTOR_CALIBRATION.md) for straightness and turning calibration.
