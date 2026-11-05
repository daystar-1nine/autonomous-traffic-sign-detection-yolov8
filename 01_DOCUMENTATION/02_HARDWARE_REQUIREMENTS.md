# 02 - Hardware Requirements & Verification Checklist

This document specifies the required hardware specifications, electrical ratings, and a structured verification checklist for the **AI Autonomous Traffic Sign Detection Car**.

---

## 📋 Hardware Verification Checklist

> [!IMPORTANT]
> **Zero Assumptions Rule**: Before applying power, verify the exact physical specifications of your components using this checklist. Do not guess voltage ratings.

### 1. Android Smartphone (Redmi) Verification
| Specification Parameter | Expected Range | Your Verified Value | How to Check on Device |
| :--- | :---: | :---: | :--- |
| **Device Model** | Redmi Note 10 / 11 / 12 / 13 series or Redmi 9 / 10 / 12 | _________________ | *Settings → About Phone → Device Name / Model* |
| **Processor (SoC)** | Qualcomm Snapdragon / MediaTek Helio or Dimensity | _________________ | *Settings → About Phone → All Specs → Processor* |
| **RAM Capacity** | Minimum 3 GB (Recommended 4 GB – 8 GB) | _________________ | *Settings → About Phone → RAM* |
| **Android OS Version** | Android 7.0 (API 24) to Android 14 (API 34) | _________________ | *Settings → About Phone → Android Version* |
| **Camera Sensor** | Rear Main Camera (1080p @ 30 FPS minimum) | _________________ | *Camera App → Settings → Video Quality* |
| **AI Hardware Delegate** | Qualcomm Hexagon DSP / MediaTek APU or Adreno/Mali GPU | Supported in TFLite | Auto-detected by NNAPI / TFLite GPU Delegate |

### 2. Power Supply & Battery Pack
| Specification Parameter | Expected Specification | Verified Status | Safety Check |
| :--- | :--- | :---: | :--- |
| **Cell Type** | 18650 Cylindrical Lithium-ion (Rechargeable) | [ ] Verified | Never use swelling or damaged cells. |
| **Configuration** | **2S1P (2 Cells in Series)** | [ ] Verified | 2 cells in series produce nominal 7.4V. |
| **Nominal Voltage** | **7.4 V DC** (3.7V per cell) | [ ] Verified | Measure with multimeter before switch. |
| **Full Charge Voltage** | **8.4 V DC** (4.2V per cell) | [ ] Verified | Disconnect charger when 8.4V is reached. |
| **Cutoff Voltage** | **6.0 V DC** (3.0V per cell) | [ ] Verified | Recharge if voltage drops below 6.2V. |
| **Capacity** | 2,000 mAh to 2,600 mAh | [ ] Verified | Provides ~45–60 minutes continuous driving. |

### 3. DC Gear Motors (TT Motors)
| Specification Parameter | Rating | Notes |
| :--- | :---: | :--- |
| **Nominal Operating Voltage** | 3.0 V – 6.0 V DC | Powered directly from 7.4V battery via TB6612 PWM duty-cycle. |
| **Gear Reduction Ratio** | 1:48 (Standard Yellow Dual-Shaft) | Provides optimal balance of torque and speed. |
| **No-Load Current @ 6V** | ~150 mA per motor | Idling wheels elevated above ground. |
| **Stall Current @ 6V** | **800 mA – 1.2 A per motor** | **Critical:** Peak current when wheels are physically blocked. |
| **Combined Peak Stall Current** | **1.6 A – 2.4 A** | Battery and driver must support this current without voltage collapse. |

### 4. DC-DC Step-Down Buck Converter
| Specification Parameter | Specification | Notes |
| :--- | :---: | :--- |
| **Module Model** | LM2596S or Mini360 | High-efficiency switching step-down regulator. |
| **Input Voltage Range** | 7.0 V – 24.0 V DC | Fed directly by 7.4V battery pack. |
| **Regulated Output Voltage** | **5.0 V – 5.2 V DC (Strict)** | **Must be tuned with brass screw before connecting NodeMCU!** |
| **Continuous Output Current** | 1.8 A (Mini360) / 2.0 A (LM2596) | Supplies NodeMCU (~150mA) and TB6612 logic (~2mA). |

### 5. TB6612FNG Dual H-Bridge Motor Driver
| Pin / Parameter | Rating / Connection | Function |
| :--- | :---: | :--- |
| **VM (Motor Voltage)** | 4.5 V – 15.0 V DC | Connects directly to Battery (+) through power switch. |
| **VCC (Logic Voltage)** | 2.7 V – 5.5 V DC | Connects to 5.0V output of Buck Converter. |
| **Continuous Output Current** | 1.2 A per channel | Safely drives TT motor operating current. |
| **Peak Surge Current** | 3.2 A per channel | Easily handles instantaneous motor stall spikes. |
| **Standby Pin (STBY)** | Active HIGH | Must be driven HIGH by ESP8266 D8 to enable motors. |

---

👉 **Next Step:** Proceed to [`03_COMPONENTS.md`](03_COMPONENTS.md) for detailed component overviews.
