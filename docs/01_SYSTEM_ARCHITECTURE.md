# 01. SYSTEM ARCHITECTURE & DESIGN PRINCIPLES
**Autonomous AI Traffic Sign Detection Car — Dual-Mode System**
**Primary AI Platform:** Samsung Galaxy A36 5G (Qualcomm Snapdragon 6 Gen 3)
**Embedded Actuator:** NodeMCU ESP8266 (ESP-12E) + TB6612FNG Dual Driver
**Manual Controller:** Cosmic Byte Ares Pro Gamepad (Bluetooth HID)

---

## 1. System Vision & Objective

The Autonomous AI Traffic Sign Detection Car is a robotic vehicle combining cutting-edge edge computer vision with real-time embedded motor control. The vehicle supports **dual-mode driving**:
1. **Autonomous AI Mode:** The mounted smartphone camera continuously captures the road, detects road signs via an edge neural network, makes autonomous navigation decisions, and drives the vehicle.
2. **Manual Gamepad Mode:** A wireless Cosmic Byte Ares Pro gamepad pairs to the smartphone via Bluetooth HID, allowing human teleoperation with progressive differential steering and dual speed profiles.
3. **Emergency Stop (Override):** A dedicated hardware failsafe that immediately halts all motor motion, overrides any active autonomous or manual commands, and holds the vehicle stationary.

---

## 2. High-Level Architecture & Separation of Concerns

```
+----------------------------------------------------------------------------------------+
|                                  PERCEPTION & BRAIN LAYER                              |
|                                (Samsung Galaxy A36 5G)                                 |
|                                                                                        |
|   [ CameraX 60 FPS ]                    [ Cosmic Byte Ares Pro Wireless Controller ]   |
|           |                                                  | (Bluetooth 5.3 HID)     |
|           v                                                  v                         |
|   [ Neural Detector ]                                [ AresProController ]             |
|   (LiteRT / TFLite / ONNX)                                   | (Axes, Triggers, D-Pad) |
|   (Adreno 710 GPU / Hexagon NPU)                             v                         |
|           |                                       [ DifferentialDriveController ]      |
|           v                                       (S-Curve Ramping, Skid Steer)        |
|   [ DecisionEngine ]                                         |                         |
|   (Debouncing, Persistence)                                  v                         |
|           |                                       [ Manual Command Generator ]         |
|           +---------------------------+----------------------+                         |
|                                       v                                                |
|                             [ ControlModeManager ]                                     |
|                    (MANUAL / AUTONOMOUS / EMERGENCY_STOP)                              |
|                                       |                                                |
|                                       v                                                |
|                             [ UdpVehicleClient ]                                       |
|                         (UDP Port 8888, Non-blocking)                                  |
+---------------------------------------|------------------------------------------------+
                                        | Wi-Fi 2.4 GHz UDP Packets
                                        v
+----------------------------------------------------------------------------------------+
|                                EXECUTION & ACTUATION LAYER                             |
|                                    (NodeMCU ESP8266)                                   |
|                                                                                        |
|   [ Wi-Fi SoftAP / UDP Receiver: 192.168.4.1:8888 ]                                    |
|           |                                                                            |
|           +--> [ Packet Parser ] ---> "CMD:DRIVE:<leftPwm>:<rightPwm>:<seq>"           |
|           |                    +----> "CMD:<ACTION>:<speed>:<trim>:<seq>"              |
|           |                                                                            |
|           +--> [ 1000ms Hardware Safety Watchdog ] ---> Auto-Stop on Packet Loss       |
|           |                                                                            |
|           v                                                                            |
|   [ TB6612FNG Dual H-Bridge Driver ] (10-bit PWM 0..1023, 1 kHz Switching)            |
|           |                                                                            |
|           +---------------------------+----------------------------+                   |
|                                       v                            v                   |
|                              [ Left TT Motor ]            [ Right TT Motor ]           |
+----------------------------------------------------------------------------------------+
```

### Architectural Principles:
1. **Zero AI on ESP8266:** The NodeMCU ESP8266 has only 80 KB of RAM and lacks floating-point acceleration. It strictly handles motor PWM generation, packet parsing, and safety watchdog execution.
2. **Local / Air-Gapped Operation:** All video processing, neural inference, and communication execute locally. The car requires **zero internet connection** or cloud servers to operate.
3. **Mutual Exclusion:** `ControlModeManager` guarantees that either Manual mode or Autonomous mode controls the motors, never both simultaneously. Emergency Stop unconditionally overrides everything.
4. **Failsafe Design:** Loss of Bluetooth signal, loss of Wi-Fi packets for >1000 ms, or application crash triggers immediate hardware motor braking.
