# 12 - Multi-Tier Emergency Stop & Hardware Fail-Safe Guide

---

## 1. Purpose
This document details the multi-layered Emergency Stop architecture that guarantees immediate vehicle halt under all failure conditions.

---

## 2. Emergency Stop Layers & Priority Hierarchy

```text
┌────────────────────────────────────────────────────────┐
│ LEVEL 1: Physical Controller Button X                  │
│ • Highest human operator priority                      │
│ • Bypasses all active drive algorithms                 │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ LEVEL 2: On-Screen Red E-STOP UI Button                │
│ • Dedicated touchscreen brake control                  │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ LEVEL 3: Ares Pro Bluetooth Disconnect Trap            │
│ • Intercepts controller drop; halts vehicle in <20ms   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ LEVEL 4: ESP8266 Hardware Communication Watchdog       │
│ • Embedded 1000ms timer stops motors on Wi-Fi loss     │
└────────────────────────────────────────────────────────┘
```

---

## 3. Burst Transmission Mechanism
When an Emergency Stop is triggered:
1. `ControlModeManager` immediately transitions to `EMERGENCY_STOP`.
2. `DifferentialDriveController.reset()` sets all local targets to zero.
3. `UdpVehicleClient.emergencyStop()` transmits a burst of **3 consecutive STOP datagrams** spaced 20ms apart.
4. This ensures delivery even if one Wi-Fi packet is dropped due to RF interference.

---

## 4. Unlocking After Emergency Stop
Once engaged, the car is strictly locked in STOP state:
- To resume **Manual Driving:** Press **Button A** on the controller or tap **MANUAL (A)** on screen.
- To resume **Autonomous Driving:** Press **Button B** on the controller or tap **AUTO (B)** on screen.

---

## 5. Verification Checklist
- [ ] Pressing Button X stops wheels instantly.
- [ ] Tapping on-screen E-STOP stops wheels instantly.
- [ ] Powering off the controller halts wheels within 1 frame.
- [ ] Disconnecting phone Wi-Fi triggers ESP8266 watchdog halt within 1.0 second.
