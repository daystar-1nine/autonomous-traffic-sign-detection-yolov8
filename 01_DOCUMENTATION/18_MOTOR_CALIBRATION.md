# 18 - Motor Tuning, Steering Calibration & Encoder Analysis

This document provides a rigorous calibration procedure to eliminate straight-line motor drift, achieve accurate 90° turns, and evaluate the role of wheel encoders in open-loop vs closed-loop robotics.

---

## ⚙️ The Open-Loop Reality: Time-Based Control vs Friction

> [!IMPORTANT]
> **Engineering Honesty Principle**: Time-based motor commands (`drive for 0.85s`) do **not** guarantee an exact 90.0° turn across all conditions. The true turn angle varies based on:
> 1. Surface friction (smooth tiles vs wooden laminate vs carpet).
> 2. Battery pack voltage (8.4V full charge vs 7.0V depleted charge).
> 3. TT motor mechanical tolerances ($\pm 10\text{--}15\%$ RPM variance between gearboxes).

To achieve reliable autonomous navigation, follow this calibration procedure.

---

## 📏 Procedure 1: Straight-Line Drift Calibration (Motor Trim)

TT motors almost never rotate at the exact same speed at equal PWM due to slight friction differences in the molded plastic spur gears.

### Step-by-Step Calibration:
1. Place the car on a flat surface along a 3-meter straight tape line.
2. In the Python test tool or Android app, issue a forward cruise command (`PWM 700`).
3. Observe vehicle deviation over a 2-meter run:
   - **Case A: Car veers to the LEFT** $\rightarrow$ Right motor is faster than Left motor.
     - *Correction:* Increase **Trim to Positive** (e.g. `trim = +8`). In the PC HUD, press `]` to increase right-motor trim.
   - **Case B: Car veers to the RIGHT** $\rightarrow$ Left motor is faster than Right motor.
     - *Correction:* Decrease **Trim to Negative** (e.g. `trim = -8`). In the PC HUD, press `[` to decrease left-motor trim.
4. Once the car tracks straight over 2.5 meters, record this trim value in `esp8266_firmware.ino` or in the Android `UdpVehicleClient.currentTrim`.

---

## 🔄 Procedure 2: 90-Degree Turn Duration Calibration

The car uses **differential skid steering**:
- Turn Left: Left wheel reverses at half speed, Right wheel drives forward at full speed.
- Turn Right: Left wheel drives forward at full speed, Right wheel reverses at half speed.

### Calibrating Turn Duration ($T_{\text{turn}}$):
1. Place the car facing directly along a reference floor tile seam ($0^\circ$).
2. Trigger a calibration test turn:
   - In PC HUD: Press **`T`**.
   - Or send UDP packet: `CMD:LEFT:760:0:1` followed by `CMD:STOP:0:0:2` after $0.85\text{ seconds}$.
3. Measure final angle relative to seam:
   - If car rotated $< 90^\circ$ (understeered): **Increase** `turnDurationMs` by $50\text{ ms}$ (e.g. $850\text{ms} \rightarrow 900\text{ms}$).
   - If car rotated $> 90^\circ$ (oversteered): **Decrease** `turnDurationMs` by $50\text{ ms}$ (e.g. $850\text{ms} \rightarrow 800\text{ms}$).
4. Update `turnDurationMs` in `DecisionEngine.kt`.

---

## 🔬 Wheel Encoders: Analysis & Future Integration

To achieve millimeter-accurate distance tracking and closed-loop PID velocity control:

### How to Add Optical Wheel Encoders:
1. Install a **20-slot optical encoder disc** onto the inner shaft of each TT motor.
2. Mount an **LM393 optical photo-interrupter sensor module** so the disc slots rotate through the sensor gap.
3. Connect sensor digital outputs to NodeMCU interrupt pins:
   - Left Encoder: `D5 (GPIO 14)`
   - Right Encoder: `D6 (GPIO 12)`
4. **PID Control Loop:** In ESP8266 firmware, count pulses per 50ms interval and adjust PWM duty cycle dynamically to lock wheel speeds in closed-loop synchronization.

---

👉 **Next Step:** Proceed to [`19_TESTING_GUIDE.md`](19_TESTING_GUIDE.md) to execute the formal testing protocol.
