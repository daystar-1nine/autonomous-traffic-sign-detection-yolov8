# 17. DUAL-MODE CONTROL & SAFETY ARBITRATION
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Operating Modes Overview

The vehicle operates in three strictly isolated states managed by `ControlModeManager.kt`:

1. **`MANUAL` (Ares Pro Remote Driving):**
   - Commands originate exclusively from the Cosmic Byte Ares Pro gamepad thumbsticks and buttons.
   - Autonomous vision decisions are suppressed.
   - Telemetry HUD displays active stick deflections and motor outputs.
2. **`AUTONOMOUS` (AI Vision Navigation):**
   - Commands originate exclusively from the CameraX + Neural Network inference pipeline and `DecisionEngine.kt`.
   - Bounding boxes and detected signs dictate steering, speed adjustments, and stopping.
   - Manual thumbstick movements are ignored (except for the Emergency Stop button).
3. **`EMERGENCY_STOP` (Safety Override):**
   - Unconditionally overrides both Manual and Autonomous modes.
   - Immediately transmits zero-velocity brake packets (`CMD:DRIVE:0:0:seq` and `CMD:STOP:0:0:seq`).
   - Hardware active braking locks motor armatures.
   - Requires explicit user intervention on the touchscreen or gamepad to unlock.

---

## 2. Finite State Machine (FSM) Diagram

```
                 +--------------------------+
                 |      POWER-ON RESET      |
                 +--------------------------+
                               |
                               v
                     [ EMERGENCY_STOP ] <------------------+
                     (Vehicle Locked)                       |
                               |                            |
                     [Unlock Button (X/HUD)]                |
                               |                            |
                               v                            |
                      [ MANUAL MODE ]                       |
                      (Ares Pro Active)                     |
                        ^           |                       |
     [Button A (Manual)]|           |[Button B (Auto)]      | [Emergency Stop]
                        |           v                       | (Button X / HUD /
                      [ AUTONOMOUS MODE ]                   |  Controller Disconnect /
                      (AI Vision Active)                    |  Link Timeout >1000ms)
                               |                            |
                               +----------------------------+
```

---

## 3. Preemption Rules & Safety Arbitration

1. **Single Control Source Rule:** Only one control subsystem can generate driving commands at any moment. This guarantees that conflicting commands (e.g., human operator pulling back while AI commands forward) cannot produce erratic motor behavior.
2. **Controller Disconnection Failsafe:** If the Ares Pro gamepad loses Bluetooth connection while the car is driving in `MANUAL` mode:
   - The Android application immediately transitions to `EMERGENCY_STOP`.
   - Zero-velocity halt packets are dispatched to the car.
   - The car will NEVER automatically revert to `AUTONOMOUS` mode without explicit user command.
3. **Autonomous Debouncing Filter:** In `AUTONOMOUS` mode, `DecisionEngine.kt` enforces temporal persistence:
   - A traffic sign must be detected across **at least 2 consecutive frames** within a 300 ms window before triggering an actuation command.
   - Single-frame lighting anomalies or optical blips are filtered out, preventing phantom stops or violent steering twitches.
