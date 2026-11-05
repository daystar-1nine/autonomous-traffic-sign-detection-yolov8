# 03 - Component Deep-Dive & Physical Specifications

This document provides a detailed technical description of each physical component in the **AI Autonomous Traffic Sign Detection Car**.

---

## 1. NodeMCU ESP8266 (ESP-12E)

```text
                  ┌───────────────┐
             A0  ─┤               ├─  D0 (GPIO 16)
            RSV  ─┤               ├─  D1 (GPIO 5) -> PWMA
            RSV  ─┤   ESP-12E     ├─  D2 (GPIO 4) -> AIN1
            SD3  ─┤   MODULE      ├─  D3 (GPIO 0) -> AIN2
            SD2  ─┤               ├─  D4 (GPIO 2) -> LED
            SD1  ─┤               ├─  3V3
            CMD  ─┤               ├─  GND
            SD0  ─┤               ├─  D5 (GPIO 14) -> BIN1
            CLK  ─┤               ├─  D6 (GPIO 12) -> BIN2
            GND  ─┤               ├─  D7 (GPIO 13) -> PWMB
            3V3  ─┤               ├─  D8 (GPIO 15) -> STBY
             EN  ─┤               ├─  RX
            RST  ─┤   [USB]       ├─  TX
            GND  ─┤               ├─  GND
            VIN  ─┴───────────────┴─  VIN (+5.0V from Buck)
```

- **Processor:** Tensilica 32-bit Xtensa LX106 @ 80/160 MHz.
- **Wi-Fi Subsystem:** Integrated 802.11 b/g/n 2.4 GHz transceiver with SoftAP capability.
- **Operating Voltage:** 3.3V internal (onboard AMS1117 regulator accepts 4.5V–9.0V on VIN pin).
- **Role in Car:** Acts as the embedded actuator controller, receiving real-time UDP commands from Android and driving TB6612FNG H-bridge inputs.

---

## 2. TB6612FNG Dual Motor Driver Module

```text
             ┌─────────────────────────────┐
        VM  ─┤ 1                        16 ├─  PWMA (Left Motor Speed)
       VCC  ─┤ 2                        15 ├─  AIN2 (Left Motor Dir 2)
       GND  ─┤ 3                        14 ├─  AIN1 (Left Motor Dir 1)
       AO1  ─┤ 4       TB6612FNG        13 ├─  STBY (Standby Enable)
       AO2  ─┤ 5      MOSFET DRIVER     12 ├─  BIN1 (Right Motor Dir 1)
       BO2  ─┤ 6                        11 ├─  BIN2 (Right Motor Dir 2)
       BO1  ─┤ 7                        10 ├─  PWMB (Right Motor Speed)
       GND  ─┤ 8                         9 ├─  GND
             └─────────────────────────────┘
```

- **MOSFET vs BJT (L298N Comparison):** Unlike the obsolete L298N which loses ~2.0V as internal heat through bipolar transistors, the TB6612FNG uses low $R_{DS(on)}$ MOSFETs. This delivers almost 100% of battery voltage directly to the TT motors for maximum torque with near-zero heat.
- **Standby Pin (STBY):** Active HIGH. When LOW, all motor outputs are disconnected (floating). Driven HIGH by NodeMCU pin D8.

---

## 3. TT DC Gearbox Motors (Yellow Motors)

- **Type:** Permanent Magnet DC Motor with plastic reduction gearbox (1:48 ratio).
- **Shaft:** Dual-flat D-shaft for slip-free wheel mounting.
- **Operating Characteristic:**
  - Forward: AO1 HIGH, AO2 LOW
  - Reverse: AO1 LOW, AO2 HIGH
  - Brake: AO1 LOW, AO2 LOW (PWM 0)
- **Role in Car:** Differential drive propulsion (Left and Right wheels).

---

## 4. DC-DC Step-Down Buck Converter (LM2596 / Mini360)

- **Type:** High-frequency switching step-down converter (up to 92% efficiency).
- **Function:** Steps down the raw 7.4V battery pack voltage to a regulated **5.1V** for NodeMCU `VIN` and TB6612FNG `VCC`.
- **Tuning:** Turn the brass multi-turn potentiometer screw counter-clockwise while observing output on a multimeter until 5.10V is reached.

---

## 5. 2S 18650 Battery Pack & Holder

- **Chemistry:** Lithium-ion ($3.7\text{V}$ nominal, $4.2\text{V}$ peak per cell).
- **Series Configuration:** 2 cells in series ($2 \times 3.7\text{V} = 7.4\text{V}$ nominal, $8.4\text{V}$ peak).
- **Role in Car:** High-current power reservoir capable of handling inductive motor surges.

---

## 6. Android Redmi Smartphone

- **Role:** Master Vision & Artificial Intelligence Brain.
- **Sensors Used:** Rear CMOS camera sensor (1080p @ 30 FPS).
- **Compute Used:** Multi-core CPU + GPU/NNAPI acceleration running on-device TFLite inference.
- **Networking:** 2.4 GHz Wi-Fi client sending UDP datagrams to `192.168.4.1:8888`.

---

👉 **Next Step:** Proceed to [`04_COMPLETE_WIRING_GUIDE.md`](04_COMPLETE_WIRING_GUIDE.md) to inspect the full circuit wiring instructions.
