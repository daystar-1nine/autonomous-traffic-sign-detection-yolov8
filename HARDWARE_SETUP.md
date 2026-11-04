# 🏎️ Hardware Wiring, Schematics & Setup Guide

This guide provides the complete hardware wiring, power distribution schematic, firmware flashing instructions, and real-time calibration steps for the **AI-Based Autonomous Traffic Sign Detection Car**.

---

## 📋 Bill of Materials (BOM)

| Component | Quantity | Purpose |
| :--- | :---: | :--- |
| **NodeMCU ESP8266 (ESP-12E)** | 1 | Microcontroller receiving AI commands over Wi-Fi & driving motors |
| **TB6612FNG Dual H-Bridge Driver** | 1 | High-efficiency MOSFET motor driver (low heat, near-zero voltage drop) |
| **TT DC Gear Motors (Yellow Motors)** | 2 | Left and Right drive wheel motors (1:48 reduction gear ratio) |
| **DC-DC Step-Down Buck Converter (LM2596 / Mini360)** | 1 | Regulates 7.4V/11.1V battery voltage down to a stable 5.0V for logic |
| **Battery Holder (2× 18650 Li-ion or 3S)** | 1 | Main vehicle power source (7.4V nominal – 8.4V peak) |
| **Drive Wheels (65mm rubber tires)** | 2 | Front or rear differential drive |
| **Omnidirectional Caster Wheel** | 1 | Front/Rear balance and frictionless 360° pivot support |
| **Robot Acrylic / 3D-Printed Chassis** | 1 | Vehicle body & mounting frame |
| **Smartphone + Phone Mount** | 1 | Live front-facing road camera stream |
| **Jumper Wires & Power Switch** | Assorted | Breadboard / soldered connections |

---

## ⚡ Power Distribution & Voltage Architecture

> [!CAUTION]
> **Common Ground Rule**: The Battery Ground (`-`), Buck Converter Ground (`GND`), NodeMCU Ground (`GND`), and TB6612FNG Ground (`GND`) **MUST all be tied together**. If Grounds are not joined, the logic signals float and motors will twitch erratically.

```text
               [ 2x 18650 Batteries (7.4V - 8.4V) ]
                               │
            ┌──────────────────┴──────────────────┐
            │ (+) Battery Raw                     │ (-) Battery GND
            ▼                                     ▼
   ┌─────────────────┐                   ┌─────────────────┐
   │ TB6612FNG (VM)  │                   │ COMMON GROUND   │
   │ [Motor Power]   │                   │ BUS             │
   └─────────────────┘                   └────────┬────────┘
            │                                     │
            ▼                                     ▼
 ┌──────────────────────┐               ┌───────────────────┐
 │ Buck Converter IN(+) │               │ Buck Converter GND│
 └──────────┬───────────┘               └─────────┬─────────┘
            │ (Adjust screw potentiometer to 5.0V)│
            ▼                                     ▼
 ┌──────────────────────┐               ┌───────────────────┐
 │ Buck OUT (5.0V Reg.) ├──┬────────────┤ Buck OUT GND      │
 └──────────────────────┘  │            └───────────────────┘
                           │
      ┌────────────────────┴────────────────────┐
      ▼                                         ▼
┌──────────────┐                        ┌──────────────┐
│ NodeMCU VIN  │                        │ TB6612FNG    │
│ (Logic 5.0V) │                        │ VCC (5.0V)   │
└──────────────┘                        └──────────────┘
```

---

## 🔌 Pin-to-Pin Wiring Diagram

### 1. NodeMCU ESP8266 to TB6612FNG Motor Driver

| NodeMCU Pin | GPIO Pin | TB6612FNG Pin | Description |
| :---: | :---: | :---: | :--- |
| **D1** | GPIO 5 | **PWMA** | Left Motor Speed Control (PWM 0 – 1023) |
| **D2** | GPIO 4 | **AIN1** | Left Motor Direction Pin 1 |
| **D3** | GPIO 0 | **AIN2** | Left Motor Direction Pin 2 |
| **D5** | GPIO 14 | **BIN1** | Right Motor Direction Pin 1 |
| **D6** | GPIO 12 | **BIN2** | Right Motor Direction Pin 2 |
| **D7** | GPIO 13 | **PWMB** | Right Motor Speed Control (PWM 0 – 1023) |
| **D8** | GPIO 15 | **STBY** | Standby Enable (Must be HIGH for driver to run) |
| **VIN** | 5V Input | **VCC** | Driver Logic Power (+5.0V from Buck Converter) |
| **GND** | Ground | **GND** | Logic Ground (Tie to Common Ground) |

### 2. TB6612FNG to Power & Motors

| TB6612FNG Pin | Connects To | Voltage / Purpose |
| :---: | :--- | :--- |
| **VM** | Battery Raw Positive (`+`) | **7.4V – 12V** (Provides high torque directly to motors) |
| **VCC** | Buck Converter Output (`+`) | **5.0V** (Powers internal driver logic) |
| **GND** (both pins) | Common Ground Bus (`-`) | System Ground Reference |
| **AO1 & AO2** | Left TT DC Motor | Left wheel drive wires |
| **BO1 & BO2** | Right TT DC Motor | Right wheel drive wires |

---

## 🛠️ Step 1: Flashing NodeMCU ESP8266 Firmware

1. Install the [Arduino IDE](https://www.arduino.cc/en/software).
2. Go to **File → Preferences**, and in **Additional Board Manager URLs**, paste:
   ```text
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
3. Go to **Tools → Board → Boards Manager**, search for `ESP8266`, and install **esp8266 by ESP8266 Community**.
4. Open the project firmware file:
   [`firmware/esp8266_car/esp8266_car.ino`](firmware/esp8266_car/esp8266_car.ino)
5. Configure your Wi-Fi:
   - **Station Mode (Recommended)**: Change `STA_SSID` and `STA_PASSWORD` to your phone's Wi-Fi hotspot credentials.
   - **Access Point Mode**: Set `#define USE_STATION_MODE 0`. The car will broadcast its own network (`AutonomousCar_AP`, password: `12345678`) with default IP `192.168.4.1`.
6. Select **Tools → Board → NodeMCU 1.0 (ESP-12E Module)** and select your COM port.
7. Click **Upload**.
8. Open the Serial Monitor (`115200` baud) to observe the assigned IP address (e.g., `192.168.137.45`).

---

## 📱 Step 2: Smartphone Camera Setup

1. Mount your smartphone securely to the front of the car chassis at a **10°–15° upward tilt**.
2. Install **DroidCam Wireless Webcam** or **IP Webcam** from Google Play Store or App Store.
3. Open the camera app and ensure the video resolution is set to **640×480** or **1280×720** for lowest streaming latency.
4. Note the video URL displayed on the phone screen:
   - Example: `http://192.168.137.1:4747/video`

---

## 🚗 Step 3: Launching the Autonomous Vision Controller

Once the car is powered on and the phone stream is active, run the master AI controller on your laptop:

```bash
# Activate your project environment
cd "S:/Kaushalya 2.0/R with CV"

# Launch Autonomous Vehicle AI Brain
python src/car_controller.py --stream-url "http://192.168.137.1:4747/video" --esp-ip "192.168.137.45" --conf 0.65
```

### 🎮 Live Cockpit HUD Keyboard Controls:
- **`M`** : Toggle between **Autonomous AI Driving** and **Manual Keyboard Driving**.
- **`SPACE`** : **Instant Emergency Brake** (Immediately stops motors).
- **`W / A / S / D`** : Steer car manually during Manual mode.
- **`+ / -`** : Dynamically increase/decrease sign detection confidence threshold.
- **`Q / ESC`** : Safely stop car and disconnect camera stream.

---

## 🎯 Autonomous Behavior & Maneuver Logic

| Detected Sign | Vehicle State | Controller Action |
| :---: | :---: | :--- |
| **`straight_ahead`** | `CRUISING` | Drives forward along the track at calibrated cruise speed (PWM 700). |
| **`left_turn`** | `TURNING` | Decelerates upon approach; executes skid-steer left turn for 0.85s once in action zone, then smoothly realigns straight. |
| **`right_turn`** | `TURNING` | Decelerates upon approach; executes skid-steer right turn for 0.85s once in action zone, then smoothly realigns straight. |
| **`stop`** | `STOPPED` | Engages regenerative braking; holds position for 3.0 seconds at the stop line; resumes cruising once clear. |
| **`no_entry`** | `EMERGENCY_STOP` | Prohibits entry immediately; halts vehicle before restricted boundary. |
| **`dead_end`** | `EMERGENCY_STOP` | Stops at track boundary and triggers safe turnaround maneuver. |

---

## 📐 Tuning & Field Calibration Tips

1. **Straight Line Drift Calibration**:
   - If the car drifts slightly left or right while moving forward, adjust `setLeftMotor` or `setRightMotor` PWM multipliers in `esp8266_car.ino` by $\pm 5\%$ to compensate for slight TT motor gearbox variations.
2. **Turn Angle Calibration**:
   - The `--turn-duration` parameter controls how long the car spins during a turn.
   - For an exact $90^\circ$ turn on tiles/carpet, tune `--turn-duration 0.75` to `0.95`.
3. **Fail-Safe Watchdog**:
   - The ESP8266 firmware has a built-in **1.2-second watchdog timer**. If Wi-Fi packets stop arriving from the laptop for more than 1.2s, the motors will auto-stop automatically so the car never crashes.
