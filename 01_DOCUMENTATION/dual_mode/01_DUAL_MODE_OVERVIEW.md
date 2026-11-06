# 01 - Dual-Mode System Architecture Overview

### *Manual Cosmic Byte Ares Pro + Autonomous AI Vision Dual-Mode Driving*

---

## 1. Purpose
This document explains the high-level architecture and operational principles of the Dual-Mode Autonomous AI Car. It unifies manual wireless gamepad teleoperation with autonomous camera-based neural network navigation onto a single robotic platform.

---

## 2. Requirements
- **Hardware:**
  - Android Smartphone (Redmi) with Bluetooth 5.0 and Wi-Fi 802.11 b/g/n.
  - Cosmic Byte Ares Pro Wireless Gamepad.
  - NodeMCU ESP8266 ESP-12E.
  - TB6612FNG Dual H-Bridge Motor Driver.
  - 2x TT DC Gear Motors.
  - 7.4V/11.1V Li-ion Battery & Buck Converter (5.15V).
- **Software:**
  - Android Studio (App v2.1 with Dual-Mode Cockpit HUD).
  - ESP8266 Firmware v2.1 (Dual-Protocol UDP Receiver).

---

## 3. System Architecture & Information Flow

```text
[ Cosmic Byte Ares Pro ]
          │  Bluetooth 5.0 HID Input Events (<8ms)
          ▼
[ Android Smartphone (Redmi) ]
    ├─► Native AresProController (Axis decoding & deadband)
    ├─► DifferentialDriveController (Slew-rate ramping & profile scaling)
    ├─► CameraX + YOLOv8n Neural Engine (1080p @ 30 FPS)
    ├─► DecisionEngine (Temporal debounce & distance zones)
    ├─► ControlModeManager (Single-source command ownership & failsafes)
    └─► UdpVehicleClient (Sub-3ms UDP socket on Port 8888)
          │  Wi-Fi UDP Datagrams: "CMD:DRIVE:..." or "CMD:ACTION:..."
          ▼
[ NodeMCU ESP8266 ]
    ├─► Dual-Protocol UDP Server
    ├─► 1000ms Hardware Watchdog Timer
    └─► PWM Motor Controller (1 kHz smooth frequency)
          │  Dual H-Bridge Logic
          ▼
[ TB6612FNG Driver ➔ 2x TT DC Motors ]
```

---

## 4. Exact Operational Modes
1. **EMERGENCY STOP (Default Boot State):**
   - Both motors hard-braked (PWM = 0).
   - All movement commands rejected until explicit unlock.
2. **MANUAL MODE:**
   - Ares Pro controller commands motors via differential steering.
   - AI camera runs for telemetry overlay only; does not actuate motors.
3. **AUTONOMOUS MODE:**
   - Neural network detects road traffic signs.
   - Decision engine generates steering, speed adjustments, and regulatory stops.
   - Gamepad movement input ignored; E-STOP button (X) remains active.

---

## 5. Expected Output
- Seamless toggling between Manual and Autonomous driving via physical gamepad buttons (`A` and `B`) or on-screen touch buttons.
- Sub-3ms latency between gamepad joystick movement and physical wheel rotation.

---

## 6. Common Errors & Troubleshooting
| Error | Cause | Immediate Resolution |
| :--- | :--- | :--- |
| Car moves in both modes simultaneously | ControlModeManager bypassed | Verify `ControlModeManager.isAutonomous()` gates all AI commands. |
| Gamepad not detected | Controller in PC/XInput dongle mode | Switch to Android Bluetooth pairing mode (`Home + A`). |

---

## 7. Verification Checklist
- [ ] Android phone detects Cosmic Byte Ares Pro over Bluetooth.
- [ ] ESP8266 SoftAP online at `192.168.4.1`.
- [ ] Mode indicator transitions cleanly between `[MANUAL]`, `[AUTO]`, and `[E-STOP]`.
