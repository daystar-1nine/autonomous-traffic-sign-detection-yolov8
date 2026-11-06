# 15. ESP8266 FIRMWARE ARCHITECTURE & BOOT PIN SAFETY
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Firmware Overview & Design

The NodeMCU ESP8266 firmware is available in two compatible formats:
1. **Single-File Arduino IDE Format:** `esp8266-firmware/esp8266_firmware.ino` (Direct 1-click compile and flash via Arduino IDE).
2. **Modular PlatformIO Format:** `esp8266-firmware/src/main.cpp` + `include/` headers (Professional C++ architecture with separation into `motor_driver.h`, `pin_config.h`, `udp_protocol.h`, `watchdog.h`).

---

## 2. Boot Pin Constraints & Hardware Protections

The ESP8266 ESP-12E module requires specific voltage levels on strap pins during power-up:

| ESP8266 Pin | NodeMCU Pin | Required Boot State | Connected Hardware | Safety Guarantee |
| :---: | :---: | :---: | :--- | :--- |
| **GPIO 15** | **D8** | **Must be LOW** | TB6612 `STBY` Pin | TB6612 `STBY` has an internal pulldown resistor; guarantees safe boot into SPI Flash |
| **GPIO 0** | **D3** | **Must be HIGH** | TB6612 `AIN2` Pin | High-impedance CMOS logic gate; pulled HIGH by internal NodeMCU pull-up |
| **GPIO 2** | **D4** | **Must be HIGH** | Onboard Blue LED | Left unconnected to external circuits |

> [!WARNING]
> Never connect motor PWM outputs or low-impedance sensor outputs to GPIO 15 (D8) or GPIO 0 (D3) without verifying boot state voltage! Pulling GPIO 15 HIGH during boot forces the ESP8266 into SDIO boot mode, preventing firmware execution.

---

## 3. High-Efficiency Motor Control Logic

The firmware interfaces with the TB6612FNG using 10-bit hardware PWM (`analogWriteFreq(1000)`):

```cpp
void applyMotors(int leftSpeed, bool leftFwd, int rightSpeed, bool rightFwd) {
    digitalWrite(PIN_AIN1, leftFwd ? HIGH : LOW);
    digitalWrite(PIN_AIN2, leftFwd ? LOW : HIGH);
    analogWrite(PIN_PWMA, constrain(leftSpeed, 0, 1023));

    digitalWrite(PIN_BIN1, rightFwd ? HIGH : LOW);
    digitalWrite(PIN_BIN2, rightFwd ? LOW : HIGH);
    analogWrite(PIN_PWMB, constrain(rightSpeed, 0, 1023));
}
```

### Motor Braking vs. Coasting:
- **Active Braking (`stopCar()`):** Pulling both `AIN1` and `AIN2` (or `BIN1` and `BIN2`) LOW while setting PWM to 0 engages short-circuit dynamic braking on the motor armature, halting the car instantly rather than coasting into obstacles.

---

## 4. 1000ms Hardware Safety Watchdog

To prevent runaway robot conditions caused by Wi-Fi disconnection or smartphone crashes:
```cpp
if (currentAction != "STOP" && (millis() - lastHeartbeat > WATCHDOG_TIMEOUT_MS)) {
    Serial.println("[WATCHDOG] Communication timeout! Emergency auto-stop.");
    stopCar();
}
```
Every valid incoming UDP packet refreshes `lastHeartbeat = millis()`. If no packet arrives for >1,000 ms, the vehicle automatically halts.
