# 20 - Diagnostic & Troubleshooting Manual

This document provides symptoms, root causes, and verified engineering solutions for all common failure modes.

---

## 🛠️ Diagnostic Matrix

| Symptom | Probable Root Cause | Corrective Engineering Action |
| :--- | :--- | :--- |
| **NodeMCU will not boot (LED solid ON or blank)** | Boot-strap pin pulled into invalid state at power-up (e.g. GPIO 15/D8 pulled HIGH or GPIO 0/D3 pulled LOW). | 1. Ensure `STBY` is connected to D8 and not externally tied to 5V.<br>2. Ensure D3 (GPIO 0) is not grounded during power-up.<br>3. Verify Buck converter supplies $\ge 5.0\text{V}$ to `VIN`. |
| **NodeMCU restarts whenever motors start driving** | **Brownout Reset:** Motor inrush current causes battery voltage to sag momentarily below the 4.7V threshold of the 3.3V LDO. | 1. Solder a **220µF to 470µF electrolytic capacitor** directly across TB6612 `VM` and `GND`.<br>2. Increase Buck Converter output to **5.15V – 5.20V**.<br>3. Ensure battery cells are fully charged ($>7.6\text{V}$ total). |
| **Motors do not spin at all, but Wi-Fi works** | 1. TB6612 `STBY` pin is LOW.<br>2. VM rail has no power.<br>3. Common Ground is broken. | 1. Measure voltage at TB6612 `STBY`: must read $\approx 3.3\text{V}$.<br>2. Measure voltage at `VM`: must read $>7.0\text{V}$.<br>3. Verify all GND pins are tied to the same ground bus. |
| **One wheel rotates backwards when driving forward** | DC motor polarity inverted. | Swap the two motor wire leads on that motor's output terminals (`AO1/AO2` or `BO1/BO2`). |
| **Car veers off course instead of driving straight** | Mechanical gearbox variance in TT motors. | Adjust motor trim: In Python HUD press `[` or `]`; in Android code adjust `UdpVehicleClient.currentTrim` by $\pm 5\%$. |
| **High video latency on phone camera** | Camera frame buffer piling up in memory. | Ensure CameraX analysis strategy is set to `ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST`. This automatically drops stale frames and processes only the newest frame. |
| **AI detects random objects as traffic signs** | Confidence threshold set too low or geometric filtering disabled. | 1. Keep confidence threshold $\ge 0.60$.<br>2. Verify `is_valid_sign_box` enforces aspect ratio $0.45 \le W/H \le 2.2$.<br>3. Clean camera lens to eliminate diffuse lighting glare. |
| **Android phone disconnects from car Wi-Fi** | Android OS detects "No Internet Access" on the car AP and auto-switches to mobile cellular data. | On the phone Wi-Fi settings for `AutonomousCar_AP`: Tap the gear icon and check **"Treat as unmetered"** and select **"Stay connected even if no internet"**. |

---

👉 **Next Step:** Proceed to [`21_FAQ.md`](21_FAQ.md) for frequently asked questions.
