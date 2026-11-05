# 22 - Pre-Flight Launch Checklist & Engineering Sign-Off

Before running the autonomous car on a physical track, review and check off every item in this pre-flight verification list.

---

## ⚡ 1. Mechanical & Hardware Checks
- [ ] Robot chassis screws and motor mounts are tightened securely.
- [ ] Caster wheel rotates 360° freely without binding.
- [ ] Smartphone mount holds the Redmi phone firmly at a 10°–15° upward tilt.
- [ ] Smartphone camera lens is cleaned with a microfiber cloth.
- [ ] Physical power switch is easily accessible from the top or rear of the vehicle.

---

## 🔋 2. Electrical & Power Checks
- [ ] Both 18650 Li-ion cells are charged to at least 3.8V each (total pack $\ge 7.6\text{V}$).
- [ ] Multimeter test on Buck Converter `OUT (+)` reads **5.1V – 5.2V DC**.
- [ ] 220µF–470µF decoupling capacitor is soldered across TB6612 `VM` and `GND`.
- [ ] Common Ground bus connects Battery (-), Buck GND, NodeMCU GND, and TB6612 GND.
- [ ] 3A fast-blow inline fuse is installed in positive battery lead.

---

## 📶 3. Firmware & Networking Checks
- [ ] NodeMCU ESP8266 flashed with [`04_ESP8266_FIRMWARE/esp8266_firmware.ino`](../04_ESP8266_FIRMWARE/esp8266_firmware.ino).
- [ ] Serial Monitor at 115200 baud confirms Access Point `AutonomousCar_AP` online at `192.168.4.1`.
- [ ] Android phone is connected to `AutonomousCar_AP` with cellular data temporarily disabled.
- [ ] UDP latency ping test responds within $<5\text{ ms}$.

---

## 🧠 4. Artificial Intelligence & Vision Checks
- [ ] `yolov8n.tflite` model file is present in `03_ANDROID_APP/app/src/main/assets/`.
- [ ] Android CameraX preview runs smoothly at 30 FPS.
- [ ] Confidence threshold is set to $\ge 0.60$.
- [ ] Test signs from `dataset/sample_signs/` detect with $>90\%$ confidence.

---

## 🛡️ 5. Safety Checks
- [ ] Fail-safe watchdog verified: motor power cuts automatically within 1.0 second of communication loss.
- [ ] Red **EMERGENCY STOP** button is responsive on the Android HUD screen.
- [ ] Test track area is completely clear of obstacles, drop-offs, and stairs.

---

### 🎉 All Systems Go!
Flip the power switch to ON, tap **AUTO MODE** in the Android app, and observe your autonomous vehicle navigate!
