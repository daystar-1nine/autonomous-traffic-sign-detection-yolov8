# 05 - Power Distribution & Electrical Budget

This document provides the mathematical power calculations, current budget, and thermal dissipation analysis for the **AI Autonomous Traffic Sign Detection Car**.

---

## ⚡ Current & Power Budget Table

| Component | Supply Rail | Min Current | Nominal Current | Peak / Stall Current | Power Consumption |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **NodeMCU ESP8266** | 5.1V Regulated (VIN) | 50 mA | 80 mA | 170 mA (Wi-Fi TX burst) | ~0.41 W (Nominal) |
| **TB6612FNG (Logic VCC)** | 5.1V Regulated | 1 mA | 2 mA | 5 mA | ~0.01 W |
| **Buck Converter Quiescent** | 7.4V Battery | 6 mA | 8 mA | 10 mA | ~0.06 W |
| **Left TT Motor (6V PWM)** | 7.4V Battery (VM) | 120 mA | 220 mA | **1,200 mA (Stall)** | ~1.63 W (Nominal) |
| **Right TT Motor (6V PWM)** | 7.4V Battery (VM) | 120 mA | 220 mA | **1,200 mA (Stall)** | ~1.63 W (Nominal) |
| **Android Smartphone** | Internal Battery | N/A | N/A | N/A (Self-powered) | 0.0 W (From car pack) |
| **TOTAL SYSTEM BUDGET** | **7.4V Battery** | **297 mA** | **530 mA** | **2,585 mA (Peak)** | **~3.92 W (Nominal)** |

---

## 🔋 Battery Endurance & Runtime Calculation

Assuming standard **2S 18650 Li-ion cells** rated at **2,200 mAh** usable capacity:

### 1. Nominal Cruising Runtime:
$$\text{Average Current Draw } (I_{\text{avg}}) \approx 530\text{ mA} = 0.53\text{ A}$$
$$\text{Operating Time } (T) = \frac{\text{Capacity } (C)}{I_{\text{avg}}} = \frac{2,200\text{ mAh}}{530\text{ mA}} \approx 4.15\text{ hours (Continuous Bench Cruise)}$$

### 2. High-Stress Track Driving Runtime:
Under frequent turns, stop-and-go cycles, and carpet resistance ($I_{\text{active}} \approx 1,100\text{ mA}$):
$$T_{\text{field}} = \frac{2,200\text{ mAh}}{1,100\text{ mA}} \approx 2.0\text{ hours}$$

---

## 🌡️ Thermal Dissipation Analysis

### Buck Converter (LM2596 / Mini360):
- Input Voltage: $V_{\text{in}} = 7.4\text{ V}$
- Output Voltage: $V_{\text{out}} = 5.1\text{ V}$
- Output Current: $I_{\text{out}} \approx 0.18\text{ A}$ (NodeMCU + logic)
- Efficiency: $\eta \approx 88\%$
- Power Dissipated as Heat:
  $$P_{\text{loss}} = V_{\text{out}} \times I_{\text{out}} \times \left(\frac{1}{\eta} - 1\right) = 5.1 \times 0.18 \times (1.136 - 1) = 0.125\text{ W}$$
- **Result:** $0.125\text{ W}$ is negligible. The buck converter runs completely cool without requiring an external heatsink.

### TB6612FNG Motor Driver:
- $R_{DS(on)}$ per MOSFET: $\approx 0.5\,\Omega$
- Combined continuous motor current: $I = 0.44\text{ A}$
- Power Dissipated:
  $$P_{\text{loss}} = I^2 \times R_{DS(on)} = (0.44)^2 \times 0.5 \approx 0.097\text{ W}$$
- **Result:** Minimal heating. Stays comfortably below the $150^\circ\text{C}$ thermal shutdown limit.

---

👉 **Next Step:** Proceed to [`06_BATTERY_SAFETY.md`](06_BATTERY_SAFETY.md) for critical battery handling rules.
