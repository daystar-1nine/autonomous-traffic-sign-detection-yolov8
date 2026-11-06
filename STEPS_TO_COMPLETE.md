# 🚗 Complete Execution Steps: AI Autonomous & Dual-Mode Robotic Car
### *Physical Assembly, Firmware Flashing, Android Deployment, Controller Pairing & Track Testing Master Guide*

> **Project Name:** AI-Based Autonomous Car Using Real-Time Traffic Sign Detection & Dual-Mode Control  
> **Target AI Smartphone:** Samsung Galaxy A36 5G (Qualcomm Snapdragon 6 Gen 3, 8GB RAM, Adreno 710 GPU)  
> **Manual Controller:** Cosmic Byte Ares Pro Wireless Gamepad (Bluetooth 5.3 HID)  
> **Actuator Platform:** NodeMCU ESP8266 + TB6612FNG Dual Driver + 2S Li-ion Battery  
> **Status:** Production Ready (Rebuilt v2.1) | **Updated:** 2026-11-06  

---

## 📋 Execution Roadmap

Follow these 8 steps in exact serial order. Do not skip any step.

```
[ Step 1: Hardware & Tools Verification ] 
       │
       ▼
[ Step 2: Buck Converter 5.15V Calibration ] ──► (⚠️ DMM se pehle set karo taaki NodeMCU na jale)
       │
       ▼
[ Step 3: Flash ESP8266 Firmware ] ──────────► (Arduino IDE / PlatformIO se 1-click flash)
       │
       ▼
[ Step 4: Circuit Wiring & Star Ground ] ────► (TB6612FNG + Motors + Battery + Common GND)
       │
       ▼
[ Step 5: Install Android App on Samsung A36 ] ► (CameraX + LiteRT / ONNX + HUD Telemetry)
       │
       ▼
[ Step 6: Pair Cosmic Byte Ares Pro Gamepad ] ─► (Bluetooth HID Mode: [HOME] + [A])
       │
       ▼
[ Step 7: Zero-Risk Bench Test ] ────────────► (Wheels off ground: Manual + Auto + Emergency Stop)
       │
       ▼
[ Step 8: Floor Track Test & Motor Trim ] ───► (Road signs autonomous navigation & straight trim)
```

---

## Step 1: Hardware & Tools Checklist

Gather all components on your workstation:

### Car Hardware:
- [x] **NodeMCU ESP8266 (ESP-12E)**
- [x] **TB6612FNG Dual Motor Driver Module**
- [x] **2× TT DC Geared Motors** (1:48 ratio) with 2 rubber wheels
- [x] **1× Front Caster Wheel** (Ball caster for 3-point balance)
- [x] **2WD Robot Chassis** (Acrylic or 3D printed)
- [x] **LM2596 DC-DC Buck Converter**
- [x] **2S Li-ion Battery Pack** (2× 18650 cells in series with 2S BMS = 7.4V nominal / 8.4V full)
- [x] **SPST Power Switch**
- [x] **Jumper Wires** (Male-to-Female, Male-to-Male)

### AI Brain & Controller:
- [x] **Samsung Galaxy A36 5G** (Mounted securely to chassis with phone clamp at 10°–15° angle)
- [x] **Cosmic Byte Ares Pro Wireless Gamepad**

### Tools:
1. **Digital Multimeter (DMM)** — Essential for setting 5.15V
2. **Small Flathead Screwdriver** — For potentiometer tuning
3. **Micro-USB Cable** — For NodeMCU flashing
4. **USB-C Cable** — For Samsung phone app deployment
5. **Double-sided foam tape / zip ties** — For mounting modules cleanly

---

## Step 2: Buck Converter 5.15V Calibration (⚠️ CRITICAL)

> [!CAUTION]
> **DO NOT connect the NodeMCU VIN pin yet!** Buck converter modules often come preset from the factory to 12V or maximum voltage. Connecting before calibration will permanently damage the ESP8266.

1. **Connect Multimeter:** Set DMM to DC Voltage ($20\text{V}$ range). Put red probe on `OUT+` and black probe on `OUT-` of the LM2596 module.
2. **Apply Battery Power:** Connect your charged 2S battery pack (7.4V–8.4V) to `IN+` and `IN-`.
3. **Turn Potentiometer Screw:** Using your flathead screwdriver, turn the brass screw on top of the blue square potentiometer **counter-clockwise** (usually 10 to 20 full rotations) until the multimeter voltage starts dropping.
4. **Tune to Exactly 5.15V:** Fine-adjust until the screen reads **5.15V DC**.
5. **Why 5.15V?** The NodeMCU onboard 3.3V LDO requires $\ge 4.5\text{V}$ to regulate properly. Setting 5.15V prevents microcontroller brownout restarts when the ESP8266 transmits Wi-Fi bursts.
6. **Disconnect Battery:** Power off and remove battery before wiring.

---

## Step 3: Flash ESP8266 Firmware

You can use either Arduino IDE or PlatformIO:

### Option A: Arduino IDE (Easiest & Fastest)
1. Install [Arduino IDE 2.3+](https://www.arduino.cc/en/software).
2. Go to **File** -> **Preferences**. Add this URL to **Additional Boards Manager URLs**:
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
3. Go to **Tools** -> **Board** -> **Boards Manager**, search for `esp8266`, and install version **3.1.2**.
4. Open the firmware file:
   `esp8266-firmware/esp8266_firmware.ino`
5. Connect your NodeMCU to PC via Micro-USB.
6. Under **Tools**, set:
   - **Board:** `NodeMCU 1.0 (ESP-12E Module)`
   - **Upload Speed:** `115200` (or `921600`)
   - **Port:** Select your NodeMCU COM port (e.g. `COM3` / `COM4`)
7. Click **Upload** (Arrow icon).
8. Open Serial Monitor at **115200 baud**. Confirm you see:
   ```
   [WIFI] Access Point Started: AutonomousCar_AP
   [WIFI] Car IP Address: 192.168.4.1
   [UDP] Listening on Port 8888
   ```

---

## Step 4: Hardware Assembly & Complete Circuit Wiring

Mount motors, driver, buck converter, battery, and NodeMCU onto the chassis, then wire according to this verified table:

### 4.1 Pin Interconnect Table

| TB6612FNG Pin | Connects To | Signal / Wire Type | Function |
| :---: | :---: | :---: | :--- |
| **PWMA** | **NodeMCU D1** (GPIO 5) | Jumper Wire | Left Motor Speed (PWM 0–1023) |
| **AIN1** | **NodeMCU D2** (GPIO 4) | Jumper Wire | Left Motor Direction 1 |
| **AIN2** | **NodeMCU D3** (GPIO 0) | Jumper Wire | Left Motor Direction 2 |
| **BIN1** | **NodeMCU D5** (GPIO 14) | Jumper Wire | Right Motor Direction 1 |
| **BIN2** | **NodeMCU D6** (GPIO 12) | Jumper Wire | Right Motor Direction 2 |
| **PWMB** | **NodeMCU D7** (GPIO 13) | Jumper Wire | Right Motor Speed (PWM 0–1023) |
| **STBY** | **NodeMCU D8** (GPIO 15) | Jumper Wire | Standby Enable (Active HIGH) |
| **VCC** | **NodeMCU 3V3** | Red Wire | Logic Power (3.3V) |
| **GND** | **Common Ground** | Black Wire | Signal Ground Reference |
| **VM** | **Battery (+) Switch Out** | Red Wire | Motor Power (7.4V–8.4V direct) |
| **AO1 / AO2** | **Left TT Motor** | Wires to Motor | Left Wheel Drive |
| **BO1 / BO2** | **Right TT Motor** | Wires to Motor | Right Wheel Drive |

### 4.2 Power Connections & Common Star Ground
- **Battery (+) (7.4V–8.4V)** ──> Switch ──> LM2596 `IN+` AND TB6612FNG `VM`
- **LM2596 `OUT+` (5.15V)** ──> NodeMCU `VIN` pin
- **Common Star Ground (GND):**
  - Battery `(-)`
  - LM2596 `IN-` and `OUT-`
  - NodeMCU `GND`
  - TB6612FNG `GND`
  > **Connect all ground wires together to a single common point.**

---

## Step 5: Android App Setup & Deployment (Samsung A36 5G)

1. Open **Android Studio** on your PC.
2. Select **Open an Existing Project** -> Navigate to `android-app/`.
3. Allow Gradle to sync dependencies.
4. On your **Samsung Galaxy A36 5G**:
   - Go to **Settings** -> **About Phone** -> **Software Information** -> Tap **Build Number** 7 times to enable Developer Mode.
   - Go to **Settings** -> **Developer Options** -> Turn ON **USB Debugging**.
5. Connect phone to PC via USB-C cable.
6. In Android Studio, select your phone in the top device toolbar and press **Run (Shift+F10)**.
7. Once installed on the phone, grant all runtime permissions (**Camera**, **Bluetooth Connect/Scan**, **Wi-Fi**).

---

## Step 6: Pair Cosmic Byte Ares Pro Gamepad

1. **Power Off Controller:** Ensure all lights on the Ares Pro are OFF.
2. **Enter Android Bluetooth Pairing Mode:**
   - Press and hold **[HOME] + [A]** simultaneously for 3 seconds.
   - The indicator LED will flash rapidly.
3. **Connect on Phone:**
   - On Samsung A36 5G, go to **Settings** -> **Bluetooth** -> Tap **Scan**.
   - Tap **"Cosmic Byte Ares Pro"** or **"Wireless Controller"** to pair.
   - The controller LED will turn solid.
4. **Verify in App:**
   - Open the **Autonomous AI Car** app.
   - The top HUD telemetry will show: `GAMEPAD: CONNECTED (Ares Pro)`.
   - Wiggle the left thumbstick: The live diagnostic overlay will display your deflection coordinates $(X, Y)$.

---

## Step 7: Zero-Risk Bench Testing (Wheels Off Ground)

Place the robot car on top of a cup, block, or box so its wheels are suspended in the air.

1. **Power On the Vehicle:** Flip the car's power switch ON.
2. **Connect Phone to Car Wi-Fi:**
   - On your Samsung A36 5G, go to Wi-Fi settings.
   - Connect to **`AutonomousCar_AP`** (Password: `car12345678`).
   - If Android says "Internet not available", tap **Keep connection**.
3. **Test Manual Teleoperation:**
   - Open the app.
   - Press **Button A** on the controller -> HUD turns Blue: `MODE: MANUAL`.
   - Push left stick forward -> Both wheels rotate forward.
   - Pull stick back -> Both wheels rotate in reverse.
   - Push stick left/right -> Left and right wheels turn differentially.
   - Press **Button Y** -> Cycles speed profile: `ECO` (50%) -> `NORMAL` (75%) -> `SPORT` (100%).
4. **Test Emergency Failsafe:**
   - While wheels are spinning, press **Button X** -> Wheels stop instantly in $<150\text{ ms}$.
   - While wheels are spinning, turn OFF the controller -> Vehicle halts immediately.

---

## Step 8: Floor Track Autonomous Test & Motor Tuning

1. **Place Car on Ground:** Set the car on a smooth floor or open hallway.
2. **Set Up Traffic Signs:**
   - Print or display standard signs (located in [`05_PYTHON_TOOLS/test_images/`](file:///s:/Kaushalya%202.0/R%20with%20CV/05_PYTHON_TOOLS/test_images/) or on a tablet/screen).
   - Place a `straight_ahead` sign at 2.5 meters.
   - Place a `stop` sign at 1.0 meter.
3. **Engage Autonomous Mode:**
   - Tap **AUTONOMOUS** on the phone screen or press **Button B** on the Ares Pro controller.
   - HUD turns Green: `MODE: AUTONOMOUS`.
4. **Observe Autonomous Driving:**
   - The app draws a green bounding box with confidence score $\ge 0.70$.
   - Car cruises forward toward `straight_ahead`.
   - Upon approaching `stop`, car stops smoothly and holds brakes for 3 seconds.
5. **Straight-Line Motor Trim (If Car Drifts Left or Right):**
   - If the car drifts to the **LEFT**, edit `android-app/app/src/main/java/com/autonomous/aicontrol/controller/DifferentialDriveController.kt`:
     ```kotlin
     rightTrimFactor = 0.94f // Slow down right motor slightly
     ```
   - If the car drifts to the **RIGHT**:
     ```kotlin
     leftTrimFactor = 0.92f // Slow down left motor slightly
     ```
   - Re-run app to lock in perfect straight tracking.

---

## 🏁 You Are Done!
Your Autonomous AI Traffic Sign Detection Car is fully operational with dual-mode driving.  
For technical deep-dives or troubleshooting, reference the 20 documentation guides in [`docs/`](file:///s:/Kaushalya%202.0/R%20with%20CV/docs/).
