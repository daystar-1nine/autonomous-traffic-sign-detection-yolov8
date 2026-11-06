# 14 - Dual-Mode System Troubleshooting & Diagnostic Guide

---

## 1. Purpose
This document provides a symptom-cause-solution guide for diagnosing and fixing issues related to the Cosmic Byte Ares Pro gamepad, Bluetooth link, UDP communication, and dual-mode switching.

---

## 2. Comprehensive Troubleshooting Matrix

| Symptom / Failure | Root Cause | Exact Solution |
| :--- | :--- | :--- |
| **Gamepad pairs in Android settings but app shows `[GAMEPAD: DISCONNECTED]`** | Gamepad paired under Switch or iOS mode | Unpair controller from phone. Hold **`Home + A`** for 3s until LED flashes rapidly. Re-pair under Android HID mode. |
| **Left stick UP moves car backward** | Inverted motor polarity | Swap motor wires on TB6612 (`AO1` with `AO2` or `BO1` with `BO2`), or adjust sign in `DifferentialDriveController.kt`. |
| **Car turns opposite to stick direction** | Left/Right motor channel swapped | Swap `PIN_PWMA`/`PIN_PWMB` or interchange Motor A and Motor B leads. |
| **Car twitches or creeps forward when stick is released** | Joystick center drift exceeding deadband | Open `AresProController.kt` and increase `deadbandThreshold` from `0.10f` to `0.15f`. |
| **Car resets or reboots when pushing stick to 100% full throttle** | Battery voltage dip / TT motor inrush current | 1. Solder a 470µF capacitor across TB6612 `VM` and `GND`.<br>2. Reduce `accelSlewRate` from 85 to 60.<br>3. Verify buck converter output is steady at 5.15V. |
| **Pressing B does not enter Autonomous mode** | Camera pipeline not ready or car in E-STOP | Check top bar: if camera shows black screen, grant Camera permission. If in E-Stop, press B to reset and enter Auto. |
| **High Wi-Fi latency (>50ms) or dropped packets** | Phone routing UDP packets to 4G/5G mobile data | Turn **Mobile Data OFF** on Android phone and disable "Smart Wi-Fi Switch". |
| **Controller disconnects after 60 seconds of idling** | Gamepad power-saving auto sleep | Push any thumbstick or tap Home button to wake up controller. |

---

## 3. Quick Diagnostic Verification
1. Open the Android app.
2. Check the **Side Diagnostic Telemetry Box**:
   - `Device`: Should show controller model name.
   - `L-Stick`: Should read `0.00 | 0.00` when resting.
   - `MOTORS`: Shows live calculated PWM for both wheels.
   - `CAR UDP`: Should display latency under `5ms`.

---

## 4. Final Sign-Off
If all checks pass, the dual-mode autonomous car is 100% operational and ready for track runs!
