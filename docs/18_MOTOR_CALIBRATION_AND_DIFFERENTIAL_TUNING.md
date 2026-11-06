# 18. MOTOR CALIBRATION & DIFFERENTIAL STEERING TUNING
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Physics of TT DC Motor Asymmetry

In low-cost robotics, standard hobby TT DC gear motors exhibit mechanical variances:
- Internal gear friction discrepancies (nylon spur gear tolerances).
- Commutator brush contact resistance differences.
- Magnet strength variations.

As a result, applying identical PWM signals (e.g., `PWM_LEFT = 700`, `PWM_RIGHT = 700`) often causes the robot to veer slightly to the left or right rather than driving in a straight line.

---

## 2. Software Trim Calibration Procedure

The firmware and differential controller provide independent hardware trim factors:

### Step 1: Straight-Line Road Test
1. Place the vehicle on a flat, smooth floor (tile, linoleum, or smooth asphalt).
2. Measure a straight 3-meter line using masking tape.
3. In `MANUAL` mode, push the left thumbstick straight forward and drive the car forward for 3 meters.
4. Observe the deviation:
   - If the car veers to the **LEFT**, the left motor is slower than the right motor.
   - If the car veers to the **RIGHT**, the right motor is slower than the left motor.

### Step 2: Applying Trim Correction
In `DifferentialDriveController.kt`:
```kotlin
// If veering left: Reduce right motor trim or boost left motor
controller.leftTrimFactor = 1.00f
controller.rightTrimFactor = 0.94f  // Scales right motor PWM to 94%

// If veering right: Reduce left motor trim
controller.leftTrimFactor = 0.92f   // Scales left motor PWM to 92%
controller.rightTrimFactor = 1.00f
```
Repeat until the vehicle travels 3 meters with $<5\text{ cm}$ lateral drift.

---

## 3. Skid-Steer Differential Kinematics

The differential drive algorithm converts normalized linear throttle ($v \in [-1.0, 1.0]$) and angular steering yaw ($\omega \in [-1.0, 1.0]$) into independent wheel velocities ($V_L, V_R$):

$$V_L = v + \omega$$
$$V_R = v - \omega$$

### Normalization & Clamping:
To prevent saturating the PWM range when steering at high speed:
```kotlin
val maxMagnitude = max(abs(vL), abs(vR))
if (maxMagnitude > 1.0f) {
    vL /= maxMagnitude
    vR /= maxMagnitude
}
val leftPwm = (vL * profile.maxPwm * leftTrimFactor).toInt()
val rightPwm = (vR * profile.maxPwm * rightTrimFactor).toInt()
```

### In-Place Pivot Turning:
When the throttle is zero ($v = 0$) and the thumbstick is pushed hard right ($\omega = 1.0$):
- $V_L = +1.0$ (Left wheel rotates forward)
- $V_R = -1.0$ (Right wheel rotates backward)
The car spins 360 degrees on its central axis without translating forward, enabling tight navigation around road obstacles.
