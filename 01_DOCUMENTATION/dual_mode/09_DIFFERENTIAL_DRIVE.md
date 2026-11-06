# 09 - Proportional Differential Steering & Slew Rate Limiting

---

## 1. Purpose
This document details the differential drive kinematics, joystick coordinate transforms, exponential smoothing, acceleration/deceleration ramping, and zero-crossing reversal protection implemented in `DifferentialDriveController.kt`.

---

## 2. Mathematical Kinematics

### 1. Raw Coordinates
- Normalized Left Stick $Y \in [-1.0, 1.0]$ ($Y < 0$ is UP/Forward on Android).
- Normalized Left Stick $X \in [-1.0, 1.0]$ ($X > 0$ is RIGHT).

### 2. Coordinate Transformation
$$\text{throttle} = -Y \quad (\text{forward positive})$$
$$\text{steering} = X \quad (\text{right positive})$$

### 3. Differential Wheel Velocities
$$V_{left} = \text{throttle} + \text{steering}$$
$$V_{right} = \text{throttle} - \text{steering}$$

### 4. Normalization Against Saturation
If the user steers sharply while at full forward throttle, raw velocities can reach $1.0 + 1.0 = 2.0$. To prevent clipping distortion, we normalize across the maximum magnitude:
$$\text{maxMag} = \max(1.0, |V_{left}|, |V_{right}|)$$
$$V_{left, norm} = \frac{V_{left}}{\text{maxMag}}$$
$$V_{right, norm} = \frac{V_{right}}{\text{maxMag}}$$

### 5. Profile Scaling & Independent Trim
$$PWM_{left, target} = V_{left, norm} \times PWM_{profile, max} \times \text{trim}_{left}$$
$$PWM_{right, target} = V_{right, norm} \times PWM_{profile, max} \times \text{trim}_{right}$$

---

## 3. Slew-Rate Limiting & Zero-Crossing Safety
To prevent violent inrush currents and gear stripping on the plastic TT gearboxes:
1. **Acceleration Step ($\Delta_{accel} = 85$ PWM/tick):** Progressive ramp-up.
2. **Deceleration Step ($\Delta_{decel} = 180$ PWM/tick):** Crisp, controlled braking.
3. **Zero-Crossing Reversal Protection:** If motor is spinning forward ($PWM > 0$) and the user slams the stick into reverse ($PWM < 0$), the controller ramps the current PWM down to exact **$0$** first before ramping in the reverse direction.

---

## 4. Verification Checklist
- [ ] Straight forward drive produces identical PWM on both wheels.
- [ ] Pivot turn rotates wheels in opposite directions.
- [ ] Full reversal decelerates through zero without motor jerk.
