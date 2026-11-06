# 04 - Cosmic Byte Ares Pro Button & Axis Mapping Specification

---

## 1. Purpose
This document specifies the exact mapping between the physical inputs of the **Cosmic Byte Ares Pro** controller, Android Native `KeyEvent`/`MotionEvent` codes, and the robotic vehicle driving actions.

---

## 2. Requirements
- Connected Cosmic Byte Ares Pro via Bluetooth.
- Android application with `AresProController` active.

---

## 3. Physical Input to Robotic Action Map

```text
 ┌────────────────────────────────────────────────────────┐
 │                   COSMIC BYTE ARES PRO                 │
 │                                                        │
 │     [ LB ] Speed -                  [ RB ] Speed +     │
 │                                                        │
 │        (L-STICK)                       [ Y ] Profile   │
 │        • UP: Throttle +              [X] E-STOP [B] AUTO│
 │        • DOWN: Throttle -              [ A ] MANUAL    │
 │        • LEFT: Steer Left                              │
 │        • RIGHT: Steer Right                            │
 └────────────────────────────────────────────────────────┘
```

### Table of Mappings:
| Controller Input | Android Event / Keycode | System Action | Operating State |
| :--- | :--- | :--- | :--- |
| **Left Stick Y** (Up/Down) | `MotionEvent.AXIS_Y` | Proportional Throttle (Forward / Reverse) | `MANUAL` |
| **Left Stick X** (Left/Right)| `MotionEvent.AXIS_X` | Proportional Steering (Left / Right) | `MANUAL` |
| **Button A** | `KeyEvent.KEYCODE_BUTTON_A` (96) | Enable / Unlock **MANUAL MODE** | `ALL` |
| **Button B** | `KeyEvent.KEYCODE_BUTTON_B` (97) | Enable / Unlock **AUTONOMOUS MODE** | `ALL` |
| **Button X** | `KeyEvent.KEYCODE_BUTTON_X` (99) | **GLOBAL EMERGENCY STOP (Brake)** | `PRIORITY 1` |
| **Button Y** | `KeyEvent.KEYCODE_BUTTON_Y` (100)| Cycle Speed Profile (`ECO` ➔ `NORMAL` ➔ `SPORT`) | `MANUAL` |
| **Left Bumper (LB)** | `KeyEvent.KEYCODE_BUTTON_L1` (102)| Decrease Speed Profile | `MANUAL` |
| **Right Bumper (RB)**| `KeyEvent.KEYCODE_BUTTON_R1` (103)| Increase Speed Profile | `MANUAL` |
| **Right Stick** | `MotionEvent.AXIS_Z` / `AXIS_RZ` | Diagnostic Telemetry Readout | `DIAGNOSTIC` |
| **Triggers (LT / RT)** | `MotionEvent.AXIS_LTRIGGER` / `RTRIGGER` | Diagnostic Analog Telemetry Readout | `DIAGNOSTIC` |

---

## 4. Expected Output
- Pressing `A` switches system mode to `[MODE: MANUAL]`.
- Pressing `B` switches system mode to `[MODE: AUTONOMOUS AI]`.
- Pressing `X` immediately engages `[EMERGENCY STOP (LOCKED)]`.
- Moving the Left Stick produces continuous differential wheel rotation.

---

## 5. Common Errors & Troubleshooting
| Issue | Cause | Solution |
| :--- | :--- | :--- |
| Inverted Forward/Reverse | Android Y axis is negative UP | Verified in code: `throttle = -stickY`. |
| Buttons swapped (A/B inverted) | Controller in Nintendo Switch layout | Check Ares Pro layout switch or reconfigure keycodes in `AresProController.kt`. |

---

## 6. Verification Checklist
- [ ] Button A triggers Manual mode.
- [ ] Button B triggers Autonomous mode.
- [ ] Button X locks Emergency Stop instantly.
- [ ] Button Y cycles between ECO, NORMAL, and SPORT speed profiles.
