# 01 - Start Here: Beginner's Onboarding Guide

Welcome to the **AI-Based Autonomous Traffic Sign Detection Car Project**!

This document is your master roadmap. Whether you are setting up your development computer from scratch or powering on the vehicle for the first time, follow this sequential guide to go from zero to a fully operating autonomous vehicle.

> 💡 **Looking for the master physical execution checklist?**  
> Check out **[`STEPS_TO_COMPLETE.md`](../STEPS_TO_COMPLETE.md)** for the complete step-by-step physical build, multimeter calibration, firmware flashing, and road testing guide.

---

## 🎯 What You Are Building

You are building an autonomous robotic vehicle where an **Android Smartphone (Redmi)** mounted on the chassis acts as the primary artificial intelligence vision system:
1. The smartphone camera captures live video of the track.
2. An on-device deep neural network (**YOLOv8 Nano**, 3.13M parameters) detects 6 regulatory and directional traffic signs in real-time.
3. A modular **Decision Engine** estimates sign distance and confirms detections across consecutive frames.
4. The smartphone transmits instantaneous navigation commands via **Wi-Fi UDP (<3ms latency)** directly to an **ESP8266 NodeMCU**.
5. The ESP8266 drives two DC gear motors via a **TB6612FNG** dual motor driver.
6. The entire system operates **100% locally** without needing external routers, internet, or cloud computers.

---

## ⚡ The 5-Step Rapid Deployment Flow

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ STEP 1          │     │ STEP 2          │     │ STEP 3          │
│ Hardware Wiring ├────►│ Flash ESP8266   ├────►│ Install Android │
│ & Power Checks  │     │ Firmware        │     │ AI APK          │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ STEP 5          │     │ STEP 4          │     │ STEP 4          │
│ Autonomous      │◄────┤ Verify UDP      │◄────┤ Connect Phone   │
│ Track Testing   │     │ Link            │     │ to Car Hotspot  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 📋 Step-by-Step Execution Sequence

### Phase 1: Hardware Assembly & Verification
1. Read [`02_HARDWARE_REQUIREMENTS.md`](02_HARDWARE_REQUIREMENTS.md) and verify your components.
2. Wire the circuits strictly following [`04_COMPLETE_WIRING_GUIDE.md`](04_COMPLETE_WIRING_GUIDE.md).
3. Tune your DC-DC Buck converter to **5.1V** with a multimeter before connecting the NodeMCU.
4. Tie all Ground wires to a single **Common Ground Bus**.

### Phase 2: Firmware Installation (ESP8266)
1. Follow [`13_ESP8266_SETUP.md`](13_ESP8266_SETUP.md).
2. Open [`04_ESP8266_FIRMWARE/esp8266_firmware.ino`](../04_ESP8266_FIRMWARE/esp8266_firmware.ino) in Arduino IDE.
3. Select board `NodeMCU 1.0 (ESP-12E Module)` and flash the microcontroller.
4. Verify Serial Monitor prints: `[WIFI] SoftAP Online: AutonomousCar_AP (IP: 192.168.4.1)`.

### Phase 3: Android App Setup & Installation
1. Follow [`11_ANDROID_SETUP.md`](11_ANDROID_SETUP.md) and [`12_ANDROID_INSTALLATION.md`](12_ANDROID_INSTALLATION.md).
2. Open the [`03_ANDROID_APP`](../03_ANDROID_APP) folder in Android Studio.
3. Connect your Redmi smartphone with USB Debugging enabled.
4. Build and install the APK onto the smartphone.

### Phase 4: Network Pairing
1. Power on the robot car using the main battery switch.
2. On your Redmi phone, go to **Settings → Wi-Fi**.
3. Connect to network:
   - **SSID:** `AutonomousCar_AP`
   - **Password:** `12345678`
4. The phone will receive IP address `192.168.4.2`.

### Phase 5: Autonomous Driving & Field Calibration
1. Mount the phone onto the front of the car chassis at a 10°–15° upward tilt.
2. Open the **Autonomous AI Car** app.
3. Place the car on a flat, clear test surface.
4. Switch to **AUTO MODE** and observe the car navigate according to detected signs!
5. Calibrate motor straight-line trim and turn duration using [`18_MOTOR_CALIBRATION.md`](18_MOTOR_CALIBRATION.md).

---

## 📖 Navigation Index of Guides

- **Hardware & Circuits:** Guides `02` through `06`
- **Software Installation:** Guides `07` through `14`
- **Networking & Protocols:** Guide `15`
- **Vehicle Operations:** Guides `16` through `18`
- **Testing & Troubleshooting:** Guides `19` through `22`

👉 **Next Step:** Proceed to [`02_HARDWARE_REQUIREMENTS.md`](02_HARDWARE_REQUIREMENTS.md) to inspect your physical hardware.
