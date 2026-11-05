# 04 - Complete Wiring Guide & Circuit Schematic

This document provides the full, unabridged wiring manual for the **AI Autonomous Traffic Sign Detection Car**, covering all 15 electrical connection requirements.

---

## ⚡ Master Circuit Schematic (ASCII Architecture)

```text
       ┌────────────────────────────────────────────────────────┐
       │   2x 18650 Li-ion Batteries (7.4V - 8.4V Total)        │
       └──────────────┬───────────────────────────┬─────────────┘
                      │ (+) Positive              │ (-) Negative
                      ▼                           ▼
              [ FUSE (3A FAST) ]                  │
                      │                           │
              [ POWER SWITCH ]                    │
                      │                           │
         ┌────────────┴───────────┐               │
         │ (7.4V High Current)    │               │
         ▼                        ▼               │
┌─────────────────┐     ┌──────────────────┐      │
│ TB6612FNG (VM)  │     │ Buck Converter   │      │
│ [Motor Power]   │     │ IN (+)           │      │
└────────┬────────┘     └────────┬─────────┘      │
         │                       │                │
    [CAPACITOR]         (Tuned to 5.1V DC)        │
    (220µF-470µF)                │                │
         │                       ▼                │
         │              ┌──────────────────┐      │
         │              │ Buck OUT (+)     │      │
         │              │ (5.1V Regulated) │      │
         │              └────────┬─────────┘      │
         │                       │                │
         │  ┌────────────────────┴──────────┐     │
         │  │ (+5.1V Logic Supply)          │     │
         │  ▼                               ▼     ▼
         │┌──────────────┐         ┌─────────────────────────┐
         ││ NodeMCU      │         │    COMMON GROUND BUS    │
         ││ VIN Pin      │         │   (All GNDs connected)  │
         │└──────┬───────┘         └───────────┬─────────────┘
         │       │                             │
         │       │ (Control Signals: D1-D8)    │ (All System Grounds)
         ▼       ▼                             ▼
  ┌──────────────────────────────────────────────────┐
  │           TB6612FNG Dual Motor Driver            │
  └──────────────┬────────────────────┬──────────────┘
                 │                    │
          [ AO1 & AO2 ]        [ BO1 & BO2 ]
                 │                    │
                 ▼                    ▼
         Left TT DC Motor     Right TT DC Motor
```

---

## 🔌 15-Point Wiring Implementation Checklist

### 1. Battery to Fuse & Main Switch
- Battery (+) terminal connects to a **3A inline fuse holder**.
- Fuse output connects to Terminal 1 of the **SPST toggle switch**.
- Terminal 2 of the toggle switch becomes the **Switched 7.4V Main Bus**.

### 2. Battery to TB6612FNG VM (Motor Rail)
- Connect Switched 7.4V Bus directly to **VM** on TB6612FNG.
- *Reason:* Motors draw up to 2.4A at stall. Feeding them directly from the battery prevents starving the microcontroller.

### 3. Battery to Buck Converter Input
- Connect Switched 7.4V Bus to **IN (+)** on the Buck Converter.
- Connect Battery (-) to **IN (-)** on the Buck Converter.

### 4. Buck Converter Output to NodeMCU VIN
- Set Buck Converter output to **5.1V – 5.2V** using potentiometer.
- Connect **OUT (+)** to NodeMCU **VIN** pin.

### 5. Logic Power to TB6612FNG VCC
- Connect Buck Converter **OUT (+)** (5.1V) to TB6612FNG **VCC**.

### 6. Common Ground Bus (CRITICAL)
Tie the following pins together on a single solder rail or breadboard strip:
1. Battery Negative (`-`)
2. Buck Converter `IN (-)` and `OUT (-)`
3. NodeMCU `GND` pin
4. TB6612FNG both `GND` pins (Pin 3 and Pin 8/9)

### 7. Left Motor Wiring
- Connect Left TT Motor terminals to **AO1** and **AO2** on TB6612FNG.
- If left wheel rotates backwards when moving forward, swap AO1 and AO2.

### 8. Right Motor Wiring
- Connect Right TT Motor terminals to **BO1** and **BO2** on TB6612FNG.
- If right wheel rotates backwards when moving forward, swap BO1 and BO2.

### 9. STBY Connection
- Connect TB6612FNG **STBY** pin to NodeMCU pin **D8 (GPIO 15)**.
- *Safety Note:* Firmware sets D8 HIGH to wake the driver. When D8 is LOW, motors are completely isolated.

### 10. Decoupling Capacitor Placement
- Solder a **220µF to 470µF 16V electrolytic capacitor** directly across TB6612FNG `VM` and `GND`.
- *Polarity:* Longer lead (+) to `VM`, shorter lead with stripe (-) to `GND`.
- *Purpose:* Absorbs inductive back-EMF and motor inrush current spikes to eliminate NodeMCU brownout reboots.

### 11. Control Signal Pin Mapping (NodeMCU to TB6612FNG)
| NodeMCU Pin | GPIO Pin | TB6612FNG Pin | Purpose |
| :---: | :---: | :---: | :--- |
| **D1** | GPIO 5 | **PWMA** | Left Motor Speed (PWM 0–1023) |
| **D2** | GPIO 4 | **AIN1** | Left Motor Direction 1 |
| **D3** | GPIO 0 | **AIN2** | Left Motor Direction 2 |
| **D5** | GPIO 14 | **BIN1** | Right Motor Direction 1 |
| **D6** | GPIO 12 | **BIN2** | Right Motor Direction 2 |
| **D7** | GPIO 13 | **PWMB** | Right Motor Speed (PWM 0–1023) |
| **D8** | GPIO 15 | **STBY** | Driver Standby Enable (Active HIGH) |

---

## ⚡ 12–15: Safety, Verification & Power-Up Sequence

### 12. Battery Polarity Verification
- Measure battery holder output with a digital multimeter before inserting 18650 cells.
- Verify RED is positive and BLACK is negative. Reverse polarity will permanently destroy the TB6612FNG and Buck converter.

### 13. Voltage Verification (Pre-Flight)
1. Turn ON the power switch **without** NodeMCU or TB6612 connected.
2. Probe Buck Converter `OUT (+)` and `OUT (-)`.
3. Verify voltage reads between **5.05V and 5.15V**. Adjust brass screw if necessary.
4. Turn OFF switch, insert NodeMCU into circuit.

### 14. Motor Current Verification
- Raise car wheels off the ground (bench test).
- Power on and trigger manual forward drive.
- Measure total system current draw: should read between **250 mA and 380 mA**.
- If current exceeds 1.5A with elevated wheels, check for mechanical gearbox binding.

### 15. Safe Power-Up Sequence
1. Ensure the phone is running the Android app and camera preview is visible.
2. Set the car on a flat surface with wheels unobstructed.
3. Flip the main physical power switch to **ON**.
4. Observe the NodeMCU blue LED flash briefly, indicating successful Wi-Fi SoftAP initialization.
5. Connect phone to `AutonomousCar_AP`.
6. Tap **AUTO MODE** to begin autonomous driving.

---

👉 **Next Step:** Proceed to [`05_POWER_DISTRIBUTION.md`](05_POWER_DISTRIBUTION.md) for electrical calculations.
