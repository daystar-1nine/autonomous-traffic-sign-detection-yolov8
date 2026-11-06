# 03. COMPONENT SELECTION & ENGINEERING TRADE-OFFS
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Motor Driver: TB6612FNG vs. L298N

A common flaw in beginner robotics projects is selecting the bulky L298N dual H-bridge. The TB6612FNG was chosen for critical engineering reasons:

| Engineering Parameter | TB6612FNG (Selected) | L298N (Rejected) | Impact on Autonomous Car |
| :--- | :--- | :--- | :--- |
| **Output Stage** | Low-RDS(on) Power MOSFETs | Bipolar Junction Transistors (BJT) | High electrical efficiency vs severe heat dissipation |
| **Internal Voltage Drop** | $\approx 0.35\text{V} - 0.5\text{V}$ | $\approx 2.0\text{V} - 2.5\text{V}$ | TB6612 delivers full battery power to TT motors |
| **Heat Dissipation** | Cool running ($<40^\circ\text{C}$); no heatsink | Burns $\approx 2\text{W}$ as heat; requires large aluminum heatsink | Reduces vehicle weight and prevents thermal brownouts |
| **Physical Dimensions** | Compact breakout ($20\text{ mm} \times 20\text{ mm}$) | Massive board ($43\text{ mm} \times 43\text{ mm} \times 27\text{ mm}$) | Leaves chassis space for phone mounting and battery |
| **Standby Mode** | Dedicated `STBY` logic pin | No standby mode; continuous quiescent draw | Enables zero-power idle mode when vehicle halts |

---

## 2. Voltage Regulation: LM2596 Buck Converter vs. Linear 7805

| Parameter | LM2596 DC-DC Buck (Selected) | LM7805 Linear Regulator (Rejected) |
| :--- | :--- | :--- |
| **Operating Principle** | High-frequency PWM switching regulator (150 kHz) | Dissipative linear voltage dropping |
| **Efficiency at 8.4V in, 5V out** | $\approx \mathbf{89\% - 91\%}$ | $\approx \mathbf{59\%}$ |
| **Wasted Thermal Power** | $\approx 0.1\text{W}$ at 1.0A load | $\approx 3.4\text{W}$ wasted as pure heat |
| **Battery Life Impact** | Adds 40–50% run time on a single battery charge | Rapid battery drain and dangerous heatsink temperatures |

---

## 3. Perception Platform: Smartphone (Samsung A36 5G) vs. SBC (Raspberry Pi 4 / Coral)

| Dimension | Samsung Galaxy A36 5G (Selected) | Raspberry Pi 4 + Pi Cam + Power Bank (Rejected) |
| :--- | :--- | :--- |
| **Total Weight on Chassis** | Single unified device (~190 grams) | Pi 4 + heatsink + camera ribbon + power bank (~380 grams) |
| **Compute Acceleration** | Qualcomm Adreno 710 GPU + Hexagon NPU | Quad-core Cortex-A72 CPU only (requires external Google Coral USB) |
| **Camera Quality** | 50 MP OIS camera with autofocus and ISP | Fixed-focus 8 MP sensor sensitive to road vibration blur |
| **Display & Cockpit** | Built-in 120 Hz AMOLED touch display for live HUD | Requires external HDMI screen, keyboard, or Wi-Fi VNC viewer |
| **Cost Efficiency** | Uses phone already owned by operator | Requires \$80-\$120 additional hardware expenditure |

---

## 4. Manual Controller: Cosmic Byte Ares Pro vs Generic Gamepad

- **Hall Effect Magnetic Triggers:** Unlike potentiometer triggers that wear down and generate erratic analog noise, Hall-effect triggers deliver frictionless, jitter-free speed scaling.
- **Low-Latency Bluetooth HID:** Connects directly to the Android OS input subsystem without requiring proprietary third-party companion apps or USB OTG dongles.
- **Ergonomics & Durability:** Dual analog thumbsticks provide fine steering resolution (10-bit internal ADC) with configurable center deadzones.
