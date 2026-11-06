# 14. COSMIC BYTE ARES PRO GAMEPAD INTEGRATION & CALIBRATION
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Controller Pairing Procedure (Bluetooth HID Mode)

To pair the Cosmic Byte Ares Pro gamepad with your Samsung Galaxy A36 5G:

1. **Power Off Gamepad:** Ensure the controller is completely powered down (all LEDs off).
2. **Activate Android HID Pairing Mode:**
   - Press and hold the **[HOME] + [A]** (or **[HOME] + [B]** depending on firmware revision) buttons simultaneously for 3 seconds.
   - The LED indicator on the controller will blink rapidly, indicating Bluetooth pairing discovery mode.
3. **Connect on Smartphone:**
   - On the Samsung Galaxy A36 5G, go to **Settings** -> **Connections** -> **Bluetooth**.
   - Tap **Scan**.
   - Look for **"Cosmic Byte Ares Pro"** or **"Wireless Controller"** under Available Devices.
   - Tap the device name and confirm pairing when prompted.
   - The controller LED will transition from rapid blinking to a solid illuminated state.

---

## 2. Default Button Mapping & Telemetry Controls

| Controller Input | Hardware Axis / Keycode | Vehicle Action / Command |
| :--- | :--- | :--- |
| **Left Thumbstick Y** | `AXIS_Y` (Inverted) | Progressive Throttle: Forward / Reverse ($-1023$ to $+1023$ PWM) |
| **Left Thumbstick X** | `AXIS_X` | Progressive Steering: Left / Right Differential Yaw |
| **Right Thumbstick X**| `AXIS_Z` / `AXIS_RZ` | Secondary Fine Steering Trim |
| **Button A** | `KEYCODE_BUTTON_A` | Engage **MANUAL MODE** (Ares Pro takes driving control) |
| **Button B** | `KEYCODE_BUTTON_B` | Engage **AUTONOMOUS MODE** (AI Camera takes control) |
| **Button X** | `KEYCODE_BUTTON_X` | Trigger **EMERGENCY STOP** (Immediate brake & lock) |
| **Button Y** | `KEYCODE_BUTTON_Y` | Cycle Speed Profile: `ECO (50%)` -> `NORMAL (75%)` -> `SPORT (100%)` |
| **Left Bumper (L1)** | `KEYCODE_BUTTON_L1`| Step Speed Profile Down |
| **Right Bumper (R1)**| `KEYCODE_BUTTON_R1`| Step Speed Profile Up |

---

## 3. Real-Time Gamepad Diagnostic HUD

When connected, the Android Cockpit HUD displays live controller telemetry:
- **Device ID & Name:** Verifies active Android `InputDevice` connection.
- **Left Stick Vector:** Displays exact $(X, Y)$ deflection floating-point coordinates.
- **Deadband Indicator:** Deflections under $0.10$ are visually flagged as `IDLE (Filtered)`.
- **Active Speed Profile:** Displays active profile and ceiling PWM clamping (`500`, `750`, or `1000`).
- **Connection Loss Watchdog:** If the controller runs out of battery or moves out of Bluetooth range, the Android app detects disconnect within 50 ms and issues an emergency halt packet.
