# 03 - Android Bluetooth Pairing Guide for Ares Pro

---

## 1. Purpose
This document provides exact step-by-step instructions for establishing a stable, low-latency Bluetooth link between the **Cosmic Byte Ares Pro** and the **Redmi Android smartphone**.

---

## 2. Requirements
- Cosmic Byte Ares Pro Controller (charged).
- Android Redmi smartphone.
- Bluetooth enabled on smartphone.

---

## 3. Setup & Exact Steps

### Step 1: Put Ares Pro into Android Pairing Mode
1. Ensure the controller is powered OFF.
2. Press and hold the **`Home + A`** buttons simultaneously for 3 seconds.
3. The LED indicator on the controller will begin flashing rapidly (Android Gamepad Mode).
*(Note: If `Home + A` does not flash, use `Home + X` for DirectInput/HID).*

### Step 2: Search on Android Phone
1. Open phone **Settings ➔ Bluetooth**.
2. Turn Bluetooth **ON**.
3. Under Available Devices, look for:
   - **`Cosmic Byte Ares Pro`** or
   - **`Wireless Controller`** or
   - **`Gamepad`**

### Step 3: Complete Pairing
1. Tap the device name to initiate pairing.
2. When prompted: *"Allow access to your contacts and phone?"* ➔ Tap **Pair**.
3. Once paired, the controller LED will become solid (LED 1 or LED 2 solid).
4. Status will show: **"Connected as input device"**.

---

## 4. Expected Output
- Solid LED indicator on controller.
- Android System Settings shows: *"Connected for input"*.
- In the Autonomous Car Android App, the top banner updates to:  
  `[GAMEPAD: Cosmic Byte Ares Pro (OK)]` (Green).

---

## 5. Common Errors & Troubleshooting
| Issue | Cause | Fix |
| :--- | :--- | :--- |
| Device pairs as audio headset | Paired under iOS/Switch mode | Forget device, hold `Home + A` to re-enter Android Gamepad mode. |
| High latency / lag | Interference or Bluetooth power saver | Disable battery optimization for the Autonomous AI Car app. |
| Disconnects after 60s | Controller sleep timeout | Move stick every 30s or check battery level. |

---

## 6. Verification Checklist
- [ ] Bluetooth device paired with name `Cosmic Byte Ares Pro` or `Wireless Controller`.
- [ ] Top HUD shows green `[GAMEPAD: Connected]`.
- [ ] Side diagnostic panel displays non-zero Vendor and Product IDs.
