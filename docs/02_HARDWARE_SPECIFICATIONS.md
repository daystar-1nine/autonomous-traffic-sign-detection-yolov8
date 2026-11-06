# 02. HARDWARE SPECIFICATIONS & DATASHEET SUMMARY
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Primary AI Vision & Computing Brain: Samsung Galaxy A36 5G

| Specification | Details | Engineering Relevance |
| :--- | :--- | :--- |
| **System on Chip (SoC)** | Qualcomm Snapdragon 6 Gen 3 (SM6475) | 4nm process; high thermal efficiency |
| **CPU Architecture** | Octa-Core: 4× 2.40 GHz Cortex-A78 + 4× 1.80 GHz Cortex-A55 | High single-thread and background throughput |
| **GPU Subsystem** | Qualcomm Adreno 710 | Vulkan 1.3, OpenCL 2.0; supports FP16 inference |
| **NPU / DSP Subsystem** | Qualcomm Hexagon NPU with Vector eXtensions (HVX) | Dedicated INT8 hardware tensor acceleration |
| **RAM & Storage** | 8 GB LPDDR4X / 128 GB UFS 2.2 | Zero buffer swapping during frame pipeline |
| **Camera Hardware** | Primary 50 MP, f/1.8 with OIS and PDAF | High dynamic range, low-light compensation |
| **Wireless Interfaces** | Wi-Fi 6 (802.11ax/ac/b/g/n) 2.4/5GHz, Bluetooth 5.3 BLE/HID | Low-latency gamepad and UDP transmission |
| **Operating System** | Android 15 with One UI / Android API 34+ | Full Jetpack CameraX & LiteRT support |

---

## 2. Robotic Chassis & Actuation Hardware

### 2.1 Microcontroller: NodeMCU ESP8266 (ESP-12E)
- **Processor:** Tensilica Xtensa 32-bit LX106 @ 80 MHz (configurable to 160 MHz).
- **SRAM:** 80 KB total data/instruction RAM (~36 KB available heap).
- **Flash Memory:** 4 MB SPI Flash.
- **Wireless Subsystem:** Integrated 802.11 b/g/n Wi-Fi transceiver with PCB trace antenna (+19.5 dBm output power).
- **PWM Output:** 10-bit resolution (range 0 to 1023), default base frequency 1,000 Hz.
- **Operating Voltage:** 3.3V logic; 5V via onboard VIN pin (fed by LM2596 buck converter).

### 2.2 Motor Driver: TB6612FNG Dual H-Bridge MOSFET Driver
- **Power Supply (VM):** 4.5V to 13.5V DC (connected directly to 2S Li-ion battery rail: 7.4V–8.4V).
- **Logic Supply (VCC):** 2.7V to 5.5V DC (connected to NodeMCU 3.3V output rail).
- **Output Current:** Continuous 1.2A per channel; peak impulse current 3.2A per channel.
- **Internal Voltage Drop:** $<0.5\text{V}$ (high-efficiency MOSFET output stages vs legacy L298N's ~2.0V bipolar drop).
- **Control Pins:** PWMA (speed), AIN1/AIN2 (direction), PWMB (speed), BIN1/BIN2 (direction), STBY (standby enable).

### 2.3 Actuators: 2× TT DC Geared Motors
- **Gear Ratio:** 1:48 dual-shaft gearbox.
- **Operating Voltage:** 3.0V to 6.0V DC (optimum nominal: 4.5V–6.0V).
- **No-Load Speed:** ~200 RPM at 6.0V.
- **No-Load Current:** ~70 mA at 6.0V.
- **Stall Current:** ~800 mA at 6.0V per motor.
- **Stall Torque:** ~0.8 kg·cm at 4.5V.

### 2.4 Power Conversion: LM2596 DC-DC Buck Converter
- **Input Voltage:** 7.0V to 35.0V DC.
- **Output Voltage:** Trimmed via multi-turn cermet potentiometer to **5.15V DC**.
- **Output Current:** Continuous 2.0A, maximum rated 3.0A with heatsink.
- **Switching Frequency:** 150 kHz internal oscillator.
- **Conversion Efficiency:** ~88% to 92%.

### 2.5 Power Source: 2S Lithium-Ion Battery Pack
- **Chemistry:** 2× 18650 Cylindrical Li-ion cells in series (2S1P).
- **Nominal Voltage:** 7.4V (3.7V per cell).
- **Full Charge Voltage:** 8.4V (4.2V per cell).
- **Cut-Off Voltage:** 6.0V (3.0V per cell; enforced by integrated 2S BMS protection circuit).
- **Capacity:** ~2,500 to 3,000 mAh per cell (~18.5 to 22.2 Wh total storage).

---

## 3. Manual Gamepad: Cosmic Byte Ares Pro
- **Connectivity:** Bluetooth 5.0 / 5.3 Low Latency HID Profile.
- **Input Layout:** Dual clickable analog thumbsticks (LS, RS), Hall-effect magnetic analog triggers (LT, RT), 8-way digital directional pad (D-Pad), 4 action buttons (A, B, X, Y), 2 shoulder bumpers (LB, RB), Menu / View navigation buttons.
- **Supported Modes:** Android Gamepad Mode (Standard HID), X-Input, D-Input.
- **Internal Battery:** 600–800 mAh rechargeable Li-ion (~10–12 hours continuous gaming).
