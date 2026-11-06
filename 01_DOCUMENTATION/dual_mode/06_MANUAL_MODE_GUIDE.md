# 06 - Manual Driving Mode Operational Guide

---

## 1. Purpose
This document provides instructions for piloting the robotic car in **Manual Driving Mode** using the Cosmic Byte Ares Pro wireless controller.

---

## 2. Requirements
- Assembled car with battery turned ON.
- Redmi phone mounted or handheld, connected to `AutonomousCar_AP` Wi-Fi (Password: `car12345678`).
- Cosmic Byte Ares Pro paired via Bluetooth.

---

## 3. Step-by-Step Operating Instructions

### Step 1: Power On & Pairing
1. Switch car power switch **ON**. Verify NodeMCU blue LED blinks once.
2. Turn ON Ares Pro gamepad. Ensure LED becomes solid (connected to Redmi phone).
3. Open **Autonomous AI Car** app on phone.

### Step 2: Unlock Manual Driving
1. On app boot, vehicle starts in `[EMERGENCY STOP (LOCKED)]`.
2. Press **Button A** on the controller (or tap orange **MANUAL (A)** button on screen).
3. The HUD transitions to: `[MODE: MANUAL]` (Orange).
4. Motor outputs are now actively mapped to the left thumbstick.

### Step 3: Driving Maneuvers
- **Forward Drive:** Gently push the Left Stick forward. Wheels accelerate smoothly forward.
- **Reverse Drive:** Pull the Left Stick backward.
- **Gradual Turning:** Push stick forward and slightly left/right. The car curves smoothly.
- **Pivot Skid Turn (Zero Turning Radius):** Push stick purely left or right without forward throttle. One wheel drives forward, the opposite wheel reverses.
- **Adjust Speed Profile:** Tap **Y** to cycle between `ECO (500)`, `NORMAL (750)`, and `SPORT (1000)`.

### Step 4: Stopping
- Release the left stick. The car decelerates cleanly to zero.
- Press **Button X** at any time to engage Emergency Brake immediately.

---

## 4. Expected Output
- Continuous, analog proportional speed control with no noticeable wireless delay (<15ms total input-to-motion latency).
- Real-time motor speed readout on the bottom HUD.

---

## 5. Common Errors & Troubleshooting
| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Motors do not respond to stick | Car locked in E-Stop | Press Button A or tap MANUAL on screen to unlock. |
| Car veers left or right on straight | TT motor manufacturing difference | Adjust `leftTrimFactor` or `rightTrimFactor` in `DifferentialDriveController.kt`. |

---

## 6. Verification Checklist
- [ ] Car drives smoothly forward and backward.
- [ ] Car turns left and right proportionally.
- [ ] Releasing stick brings motors to complete stop.
- [ ] Emergency stop button halts car instantly.
