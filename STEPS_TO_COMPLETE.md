# 🚗 Complete Execution Steps: AI Autonomous Traffic Sign Detection Car
### *Physical Assembly, Software Flashing, Calibration & Autonomous Road Testing Master Guide*

> **Project Name:** AI-Based Autonomous Car Using Real-Time Traffic Sign Detection  
> **Repository:** [autonomous-traffic-sign-detection-yolov8](https://github.com/daystar-1nine/autonomous-traffic-sign-detection-yolov8)  
> **Status:** Production Ready (Rebuilt v2.0)  
> **Last Updated:** 2026-11-06

---

## 📋 Table of Contents
1. [Overview & Execution Roadmap](#1-overview--execution-roadmap)
2. [Step 1: Required Tools & Hardware Verification](#step-1-required-tools--hardware-verification)
3. [Step 2: Buck Converter Voltage Calibration (⚠️ CRITICAL FIRST STEP)](#step-2-buck-converter-voltage-calibration-️-critical-first-step)
4. [Step 3: Flashing ESP8266 Firmware (NodeMCU)](#step-3-flashing-esp8266-firmware-nodemcu)
5. [Step 4: Mechanical Assembly & Complete Circuit Wiring](#step-4-mechanical-assembly--complete-circuit-wiring)
6. [Step 5: Android App Setup & Deployment (Redmi Phone)](#step-5-android-app-setup--deployment-redmi-phone)
7. [Step 6: Bench Testing (Wheels in the Air - Zero Risk)](#step-6-bench-testing-wheels-in-the-air---zero-risk)
8. [Step 7: Floor Track Autonomous Test & Motor Tuning](#step-7-floor-track-autonomous-test--motor-tuning)
9. [Troubleshooting & Emergency Fixes](#troubleshooting--emergency-fixes)
10. [Final Completion Checklist](#final-completion-checklist)

---

## 1. Overview & Execution Roadmap

Is project ko physically complete karne ke liye 7 logical steps follow karne hain. **Har step ko serial order me complete karein, koi bhi step skip na karein.**

```
[ Step 1: Tools Check ] 
       │
       ▼
[ Step 2: Buck Converter Calibration (5.15V) ] ──► (NodeMCU jalne se bachane ke liye pehle karo)
       │
       ▼
[ Step 3: Flash NodeMCU ESP8266 Firmware ] ──► (Arduino IDE / PlatformIO)
       │
       ▼
[ Step 4: Hardware Assembly & Full Wiring ] ──► (TB6612FNG + Motors + Battery + Common GND)
       │
       ▼
[ Step 5: Android App Install on Redmi Phone ] ──► (CameraX + YOLOv8 + UDP Control)
       │
       ▼
[ Step 6: Bench Test (Wheels Off Ground) ] ──► (Manual Mode + Direction Check + Emergency Stop)
       │
       ▼
[ Step 7: Autonomous Floor Track Run ] ──► (Traffic Signs Detection & Auto Navigation)
```

---

## Step 1: Required Tools & Hardware Verification

Apne saare components aur tools table par ready rakhein:

### Hardware Components:
- [x] **1x NodeMCU ESP8266** (ESP-12E Board)
- [x] **1x TB6612FNG** Dual Motor Driver Module
- [x] **2x TT DC Gear Motors** (3V–6V, with 2 Rubber Wheels)
- [x] **1x Caster Wheel** (Ball caster for 3-point balance)
- [x] **1x Robot 2WD Chassis** (Acrylic or 3D printed)
- [x] **1x DC-DC Buck Converter** (LM2596 with potentiometer)
- [x] **1x Battery Pack** (2x 18650 Li-ion cells in series = 7.4V nominal / 8.4V max, or 3S 11.1V)
- [x] **1x SPST Rocker Power Switch**
- [x] **1x Android Smartphone** (Redmi Phone with camera and Wi-Fi)
- [x] **1x Phone Mount / Mobile Clamp** (Mounted at 10°–15° upward angle)
- [x] **Connecting Wires** (Male-to-Female & Male-to-Male Jumper wires)
- [x] **1x 220µF to 470µF Electrolytic Capacitor** (Optional but strongly recommended across VM and GND to prevent motor reset spikes)

### Tools Required:
1. **Digital Multimeter** (Voltage measure karne ke liye)
2. **Small Flathead Screwdriver** (Buck converter potentiometer adjust karne ke liye)
3. **Micro-USB Cable** (NodeMCU flash karne ke liye)
4. **USB-C Cable** (Redmi phone me app debug/install karne ke liye)
5. **Double-sided Tape / Zip Ties** (Components securely mount karne ke liye)
6. **Printed Traffic Signs** (Found in [`dataset/sample_signs/`](file:///s:/Kaushalya%202.0/R%20with%20CV/dataset/sample_signs/))

---

## Step 2: Buck Converter Voltage Calibration (⚠️ CRITICAL FIRST STEP)

> [!CAUTION]
> **DO NOT CONNECT NodeMCU or TB6612 TO THE BUCK CONVERTER YET!**  
> Factory-set buck converters often output 12V–20V. Agar bina check kiye NodeMCU ke `VIN` pin par connect kar diya, to NodeMCU instantly jal jayega!

### Calibration Procedure:
1. Battery holder ke (+) wire ko Switch ke through Buck Converter ke **`IN+`** terminal me lagayein.
2. Battery holder ke (-) wire ko Buck Converter ke **`IN-`** terminal me lagayein.
3. Multimeter ko **DC 20V Mode** par set karein.
4. Multimeter probe:
   - **RED probe** ➔ Buck Converter **`OUT+`**
   - **BLACK probe** ➔ Buck Converter **`OUT-`**
5. Power Switch ko **ON** karein.
6. Screwdriver se Buck Converter ke golden screw (potentiometer) ko counter-clockwise (anti-clockwise) ghumayein jab tak multimeter reading exact **5.15V DC** (Safe range: 5.10V – 5.20V) na dikhaye.
7. Switch ko **OFF** karein aur multimeter hata lein.
8. Ab Buck Converter NodeMCU ko safely power dene ke liye ready hai.

---

## Step 3: Flashing ESP8266 Firmware (NodeMCU)

Car ko assemble karne se pehle NodeMCU ko flash karna sabse aasan hota hai.

### Option A: Using Arduino IDE (Recommended for Beginners)
1. Laptop me **Arduino IDE 2.x** open karein.
2. **ESP8266 Board Package Install karein** (agar nahi hai):
   - `File` ➔ `Preferences` ➔ `Additional Boards Manager URLs` me add karein:
     ```text
     http://arduino.esp8266.com/stable/package_esp8266com_index.json
     ```
   - `Tools` ➔ `Board` ➔ `Boards Manager` ➔ search `esp8266` ➔ Click **Install**.
3. Project firmware file open karein:
   - File path: [`04_ESP8266_FIRMWARE/esp8266_firmware.ino`](file:///s:/Kaushalya%202.0/R%20with%20CV/04_ESP8266_FIRMWARE/esp8266_firmware.ino)
4. NodeMCU ko Micro-USB cable se laptop se connect karein.
5. Board & Port select karein:
   - **Board:** `NodeMCU 1.0 (ESP-12E Module)`
   - **Upload Speed:** `115200`
   - **CPU Frequency:** `80 MHz` (or `160 MHz`)
   - **Port:** Apka COM port (e.g., `COM3`, `COM5`)
6. **Upload** (Arrow button) par click karein.
7. Upload complete hone ke baad **Serial Monitor** (Baud rate: `115200`) open karein aur NodeMCU ka `RST` button dabayein:
   ```text
   ========================================
   Autonomous AI Vehicle Firmware v2.0
   Boot strapping verified: Safe
   SoftAP Started: AutonomousCar_AP
   IP Address: 192.168.4.1
   UDP Listening on Port: 8888
   Watchdog: ARMED (500ms timeout)
   ========================================
   ```
8. Agar ye message dikh raha hai, to firmware successfully flash ho chuka hai!

---

## Step 4: Mechanical Assembly & Complete Circuit Wiring

### 1. Mechanical Assembly:
1. Chassis ke dono sides me TT DC Gear Motors ko screws se fix karein.
2. Dono motors me wheels attach karein.
3. Front / Rear me Caster wheel lagayein taaki car 3-point balance par smooth turn le sake.
4. Battery holder ko chassis ke center/bottom me mount karein (center of gravity low rakhne ke liye).
5. NodeMCU, TB6612FNG aur Buck Converter ko chassis ke top plate par double-sided tape ya standoffs se fix karein.

---

### 2. Exact Pin-to-Pin Wiring Table:

#### A. NodeMCU to TB6612FNG Motor Driver:
| NodeMCU ESP8266 Pin | TB6612FNG Pin | Purpose / Function | Safe Boot Note |
|---|---|---|---|
| **D1 (GPIO 5)** | **AIN1** | Motor A (Left) Direction 1 | Safe I/O |
| **D2 (GPIO 4)** | **AIN2** | Motor A (Left) Direction 2 | Safe I/O |
| **D5 (GPIO 14)**| **PWMA** | Motor A (Left) Speed PWM | Safe I/O |
| **D7 (GPIO 13)**| **BIN1** | Motor B (Right) Direction 1 | Safe I/O |
| **D6 (GPIO 12)**| **BIN2** | Motor B (Right) Direction 2 | Safe I/O |
| **D4 (GPIO 2)** | **PWMB** | Motor B (Right) Speed PWM | High at boot (Safe) |
| **3.3V** (or **D0**)| **STBY** | Standby Pin (Must be HIGH to enable motors) | High enables driver |
| **GND** | **GND** | Logic Ground | Common GND |

> [!IMPORTANT]
> **Boot Pin Safety Verified:**  
> D8 (GPIO 15) ko motor pin ke roop me use **nahi** kiya gaya hai kyunki agar D8 boot ke time HIGH ho gaya to NodeMCU flash mode me chala jayega aur boot fail ho jayega. Hamari pin configuration 100% verified hai.

---

#### B. Power Distribution & Motors:
| Source | Destination | Wire Color | Notes |
|---|---|---|---|
| **Battery (+) (7.4V / 11.1V)** | Power Switch Input | RED | Through Switch |
| **Power Switch Output** | Buck Converter **`IN+`** | RED | Regulated logic input |
| **Power Switch Output** | TB6612 **`VM`** Pin | RED | High current for TT motors directly from battery |
| **Battery (-) (GND)** | Buck Converter **`IN-`** | BLACK | Main Battery Ground |
| **Buck Converter `OUT+` (5.15V)** | NodeMCU **`VIN`** Pin | RED | Powers ESP8266 board |
| **Buck Converter `OUT+` (5.15V)** | TB6612 **`VCC`** Pin | RED | Powers TB6612 logic chips (2.7V–5.5V) |
| **Buck Converter `OUT-`** | NodeMCU **`GND`** Pin | BLACK | **Common Ground** |
| **TB6612 `GND` (All 3)** | Common Ground Bus | BLACK | Must be tied together |
| **TB6612 `AO1` & `AO2`** | Left TT Motor Terminals | Blue / Yellow | Left drive wheel |
| **TB6612 `BO1` & `BO2`** | Right TT Motor Terminals| Blue / Yellow | Right drive wheel |
| **470µF Capacitor (+)** | TB6612 **`VM`** Pin | Capacitor (+) | Absorbs motor voltage dips |
| **470µF Capacitor (-)** | TB6612 **`GND`** Pin | Capacitor (-) | Short leads close to driver |

```
                     ┌───────────────────────────────┐
                     │    2S Li-ion Battery (7.4V)   │
                     └──┬─────────────────────────┬──┘
                        │ (+)                     │ (-)
                     [SWITCH]                     │
                        │                         │
            ┌───────────┴──────────┐              │
            │                      │              │
            ▼                      ▼              ▼
     ┌─────────────┐        ┌─────────────┐  ┌─────────────┐
     │ TB6612 `VM` │        │ Buck `IN+`  │  │ Buck `IN-`  │
     └─────────────┘        └──────┬──────┘  └──────┬──────┘
                                   │ [Potentiometer]│
                                   ▼ (5.15V DC)     ▼ (Common GND)
                            ┌─────────────┐  ┌─────────────┐
                            │ Buck `OUT+` │  │ Buck `OUT-` │
                            └──┬───────┬──┘  └──────┬──────┘
                               │       │            │
            ┌──────────────────┘       └────┐       │
            ▼                               ▼       ▼
     ┌─────────────┐                 ┌─────────────┐
     │ NodeMCU VIN │                 │ TB6612 VCC  │
     └─────────────┘                 └─────────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
                    COMMON SYSTEM GND
```

---

## Step 5: Android App Setup & Deployment (Redmi Phone)

Android smartphone car ka primary AI brain hai jo live camera frames capture karta hai, YOLO model se traffic signs detect karta hai, driving decisions leta hai aur sub-3ms latency par NodeMCU ko UDP commands bhejta hai.

### 1. Developer Options Enable Karein (Redmi Phone):
1. Phone **Settings** ➔ **About Phone** me jayein.
2. **MIUI Version / OS Version** par 7 baar tap karein ("You are now a developer!").
3. **Settings** ➔ **Additional Settings** ➔ **Developer Options** me jayein:
   - Enable **USB Debugging** = `ON`
   - Enable **Install via USB** = `ON`
   - Enable **USB Debugging (Security settings)** = `ON`

### 2. Build & Install Android App:
1. Laptop me **Android Studio** open karein.
2. Open Project: select directory [`03_ANDROID_APP`](file:///s:/Kaushalya%202.0/R%20with%20CV/03_ANDROID_APP).
3. Wait for Gradle Sync to complete.
4. Model weights verify karein:
   - File [`yolov8n_traffic_signs.onnx`](file:///s:/Kaushalya%202.0/R%20with%20CV/03_ANDROID_APP/app/src/main/assets/yolov8n_traffic_signs.onnx) ya TFLite model `app/src/main/assets/` me present hona chahiye.
5. Redmi phone ko USB cable se laptop se connect karein.
6. Android Studio toolbar me Redmi device select karein aur **Run 'app' (Shift + F10)** click karein.
7. Phone screen par "Install via USB" prompt aane par **Allow** karein.
8. App launch hone par **Camera Permission** allow karein.

### 3. Screen Orientation & Settings:
- App automatically Landscape mode me start hogi.
- **Top Bar Telemetry Display Check Karein:**
  - `FPS: ~28-30`
  - `Latency: ~25-35 ms`
  - `ESP Status: SEARCHING...`
  - `Mode: MANUAL`

---

## Step 6: Bench Testing (Wheels in the Air - Zero Risk)

> [!IMPORTANT]
> **Safety Rule:** Pehla test hamesha car ko kisi box ya stand par rakh kar karein jisse dono wheels hawa me free ghum sakein. Floor par direct mat chalayein.

### Testing Sequence:

#### 1. Wi-Fi Pairing:
1. Car ka Power Switch **ON** karein.
2. Redmi phone ki **Wi-Fi Settings** open karein.
3. Available networks me **`AutonomousCar_AP`** par connect karein:
   - **Password:** `car12345678`
4. Phone me agar prompt aaye: *"This network has no internet access. Stay connected?"* ➔ **Keep Connected / Yes** select karein.
5. **Mobile Data (4G/5G)** temporarily switch **OFF** karein taaki phone UDP packets ko cellular network par route na kare.

#### 2. Manual Controls Check:
1. Car App open karein.
2. Top HUD me check karein: **`ESP Status: CONNECTED`** (Green indicator).
3. **FORWARD** button press karein:
   - Dono wheels forward direction me rotate hone chahiye.
   - *Agar koi wheel ulta ghum raha hai:* Us motor ke dono wires (AO1/AO2 ya BO1/BO2) ko aapas me swap (interchange) kar dein.
4. **REVERSE** button press karein:
   - Dono wheels reverse rotate hone chahiye.
5. **LEFT** button press karein:
   - Left wheel slow/reverse aur Right wheel forward ghumna chahiye.
6. **RIGHT** button press karein:
   - Right wheel slow/reverse aur Left wheel forward ghumna chahiye.
7. **STOP** button press karein:
   - Motors instantly stop honi chahiye.

#### 3. Watchdog Failsafe Test:
1. FORWARD button press karke car ke wheels spin karein.
2. Phone ka Wi-Fi toggle OFF karein.
3. **Verification:** Exactly **500 milliseconds** ke andar car ke dono motors automatically OFF ho jane chahiye (NodeMCU hardware watchdog action).

---

## Step 7: Floor Track Autonomous Test & Motor Tuning

Ab car physically ready hai autonomous driving ke liye!

### 1. Phone Mounting & Camera Angle:
1. Phone ko car ke front phone mount me landscape orientation me securely fix karein.
2. Camera lens bilkul clean hona chahiye.
3. Phone ko **10° se 15° upward angle** par tilt karein taaki camera aage aane wale road signs ko 1.5–3 meters door se hi dekh sake.

### 2. Sample Signs Ready Karein:
Folder [`dataset/sample_signs/`](file:///s:/Kaushalya%202.0/R%20with%20CV/dataset/sample_signs/) me diye gaye sample signs ko print kar lein ya kisi tablet/laptop screen par display karein:
- **`stop`** (Red octagonal Stop sign)
- **`left`** (Blue turn left arrow)
- **`right`** (Blue turn right arrow)
- **`speed_limit_30`** (Circular 30 limit)
- **`speed_limit_60`** (Circular 60 limit)

### 3. Track Setup:
- Ek saaf, flat floor par car ko rakhein.
- Car ke aage 1.5 meter distance par road side me **`stop`** sign place karein.

### 4. Autonomous Driving Test:
1. App me **`AUTONOMOUS MODE`** toggle button dabayein.
2. Car forward move karna start karegi (`BASE_PWM: 160`).
3. Jaise hi camera **STOP** sign ko detect karega (Confidence > 65% for 3 consecutive frames):
   - Bounding Box Green/Red ho jayega.
   - Text display hoga: `Detected: STOP (88%) -> DECISION: EMERGENCY_STOP`.
   - Car turant stop hogi aur 3 seconds tak pause rahegi.
   - 3 seconds baad car dubara forward travel resume karegi.
4. Ab **`left`** sign samne layein:
   - Decision Engine trigger karega: `DECISION: TURN_LEFT`.
   - Car smooth 45°–90° left turn legi aur normal speed par aage badhegi.
5. Ab **`speed_limit_30`** sign dikhayein:
   - Car ki speed automatically slow ho jayegi (`PWM: 120`).
6. Ab **`speed_limit_60`** sign dikhayein:
   - Car ki speed increase ho jayegi (`PWM: 200`).

---

### 5. Motor Straight-Line Trim Calibration:
Agar car seedhi chalne par left ya right drift ho rahi hai (TT motors me manufacturing variation ki wajah se minor speed difference hota hai):
1. File open karein: [`04_ESP8266_FIRMWARE/include/pin_config.h`](file:///s:/Kaushalya%202.0/R%20with%20CV/04_ESP8266_FIRMWARE/include/pin_config.h#L34-L36) ya `.ino`:
   ```cpp
   // Motor Speed Trims (1.0 = 100%, 0.95 = 95%)
   #define LEFT_MOTOR_TRIM   1.00f
   #define RIGHT_MOTOR_TRIM  0.95f  // Right motor ko thoda slow kiya agar car right bhag rahi thi
   ```
2. Re-upload firmware. Car ab straight line me smoothly chalegi!

---

## Troubleshooting & Emergency Fixes

| Problem / Symptom | Possible Cause | Solution / Fix |
|---|---|---|
| **Motor start hote hi NodeMCU reset/reboot ho jata hai** | Voltage drop (brownout) due to high motor starting current | 1. TB6612 ke `VM` aur `GND` ke beech **470µF capacitor** lagayein.<br>2. Make sure Buck converter output is strictly 5.15V. |
| **Wi-Fi Disconnect ho jata hai ya UDP Timeout hota hai** | Phone internet na hone par mobile data par switch kar raha hai | Phone me **Mobile Data OFF** karein aur Wi-Fi Settings me "Smart Network Switch" / "Auto-switch to mobile data" disable karein. |
| **Car ki motors bilkul nahi ghumti (Sirf click sound)** | TB6612 `STBY` pin LOW hai ya Battery voltage kam hai | 1. Check karein TB6612 `STBY` pin NodeMCU ke `3.3V` ya `D0` se connected ho.<br>2. Multimeter se battery voltage check karein (>7.0V hona chahiye). |
| **Car ulti direction me ghumti hai (Reverse instead of forward)** | Motor wires polarity swapped | TB6612 ke motor output pins (`AO1`/`AO2` ya `BO1`/`BO2`) par wires ko aapas me interchange karein. |
| **Android App me Camera FPS bhot low hai (<15 FPS)** | NPU acceleration off hai ya resolution bhot high hai | In `YoloDetector.kt`, make sure input image size is fixed to `640x640` and inference runs on background thread (NNAPI / GPU delegate enabled). |
| **Sign detect hota hai par car turn nahi leti** | Confidence threshold bhot high hai (>85%) ya sign bhot door hai | In `DecisionEngine.kt`, confidence threshold ko `0.55` ya `0.60` par set karein aur minimum 2 consecutive frames rakhein. |

---

## Final Completion Checklist

Final test se pehle is checklist ke har item ko checkmark karein:

- [ ] **Buck Converter calibrated to 5.15V DC** (Verified with Multimeter).
- [ ] **All grounds tied together** (Common Ground between Battery, Buck, NodeMCU, and TB6612).
- [ ] **ESP8266 flashed with v2.0 firmware** (Serial monitor shows `AutonomousCar_AP` ready).
- [ ] **Android App installed on Redmi phone** (CameraX preview active, YOLO loaded).
- [ ] **Bench test passed** (Wheels spin forward, reverse, left, right in manual mode).
- [ ] **Watchdog timeout passed** (Motors stop within 500ms if Wi-Fi disconnects).
- [ ] **Phone mounted at 10°–15° angle** on robot chassis.
- [ ] **Traffic signs printed** (STOP, LEFT, RIGHT, 30, 60).
- [ ] **Floor test passed** (Autonomous mode detects STOP sign and executes timed stop).

---

### 🎉 Congratulations!
Aapka **AI Autonomous Traffic Sign Detection Robot Car** successfully physical world me live test hone ke liye 100% ready hai!

*Documentation Links:*
- [01_START_HERE.md](file:///s:/Kaushalya%202.0/R%20with%20CV/01_DOCUMENTATION/01_START_HERE.md)
- [04_COMPLETE_WIRING_GUIDE.md](file:///s:/Kaushalya%202.0/R%20with%20CV/01_DOCUMENTATION/04_COMPLETE_WIRING_GUIDE.md)
- [16_AUTONOMOUS_MODE.md](file:///s:/Kaushalya%202.0/R%20with%20CV/01_DOCUMENTATION/16_AUTONOMOUS_MODE.md)
- [18_MOTOR_CALIBRATION.md](file:///s:/Kaushalya%202.0/R%20with%20CV/01_DOCUMENTATION/18_MOTOR_CALIBRATION.md)
