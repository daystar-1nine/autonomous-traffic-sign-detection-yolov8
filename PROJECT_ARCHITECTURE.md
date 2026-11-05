# Complete System & Software Architecture

This document defines the multi-tier engineering architecture spanning the Android mobile vision stack, wireless communications, embedded microcontroller firmware, and power distribution subsystems.

---

## 🏛️ High-Level System Architecture Diagram

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   TIER 1: MOBILE AI VISION SYSTEM                      │
│                  (Android Redmi Smartphone on Chassis)                 │
├────────────────────────────────────────────────────────────────────────┤
│  [CameraX API] ──► 1080p @ 30 FPS Stream                               │
│       │                                                                │
│       ▼                                                                │
│  [YOLOv8n Neural Engine] ──► TFLite Float16 on Mobile CPU/GPU/NPU       │
│       │                       Input: [1, 3, 640, 640]                  │
│       │                       Output: [1, 10, 8400]                    │
│       ▼                                                                │
│  [Confidence & Geometric Filter] ──► Aspect Ratio [0.45, 2.2], Conf>=0.60
│       │                                                                │
│       ▼                                                                │
│  [Temporal Debounce & Sign Tracker] ──► Consecutive Frame Confirmation │
│       │                                                                │
│       ▼                                                                │
│  [Spatial Decision Engine] ──► Proximity Zone (Far / Approach / Action)│
│       │                                                                │
│       ▼                                                                │
│  [UDP Client Engine] ──► Non-blocking Coroutine Datagram Dispatch      │
└───────┬────────────────────────────────────────────────────────────────┘
        │
        │ Wi-Fi 802.11 b/g/n (Port 8888, Sub-3ms UDP Datagrams)
        │
┌───────▼────────────────────────────────────────────────────────────────┐
│                  TIER 2: EMBEDDED ACTUATION SYSTEM                     │
│                       (NodeMCU ESP8266 ESP-12E)                        │
├────────────────────────────────────────────────────────────────────────┤
│  [SoftAP Wi-Fi Engine] ──► SSID: AutonomousCar_AP (IP: 192.168.4.1)    │
│  [UDP Packet Parser] ──► Validates Header, Command, Speed, Sequence    │
│  [Safety Watchdog Timer] ──► 1.0s Lease Timeout Auto-Stop Protection    │
│  [Motor Control Engine] ──► Soft-Start 1kHz PWM Ramp & Balance Trim    │
└───────┬────────────────────────────────────────────────────────────────┘
        │
        │ GPIO Signals: PWMA, AIN1, AIN2, BIN1, BIN2, PWMB, STBY
        │
┌───────▼────────────────────────────────────────────────────────────────┐
│                   TIER 3: POWER & ELECTROMECHANICAL                    │
├────────────────────────────────────────────────────────────────────────┤
│  [TB6612FNG Driver] ──► Dual H-Bridge MOSFETs (Up to 3.2A peak)        │
│  [2x TT Gear Motors] ──► 1:48 Reduction Gearbox Differential Drive     │
│  [DC-DC Buck Converter] ──► LM2596/Mini360 stepping 7.4V down to 5.1V  │
│  [2S 18650 Battery Pack] ──► 7.4V Nominal (8.4V Peak) with 3A Fuse     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 State Machine State Diagram

```text
               ┌───────────────┐
               │   STARTUP /   │
               │  DISCONNECTED │
               └───────┬───────┘
                       │ Wi-Fi Connected
                       ▼
               ┌───────────────┐
       ┌──────►│   CRUISING    │◄─────────────────┐
       │       │ (Forward PWM) │                  │
       │       └───────┬───────┘                  │
       │               │                          │
       │ Target Sign   │ Target Sign              │ Cooldown Expired
       │ Reaches       │ Reaches                  │
       │ Action Zone   │ Action Zone              │
       │               ▼                          │
       │       ┌───────────────┐                  │
       │       │    TURNING    ├──────────────────┘
       │       │ (Left/Right)  │ (Locks for 0.85s)
       │       └───────────────┘
       │               │
       │ Target is     │
       │ STOP Sign     ▼
       │       ┌───────────────┐
       │       │    STOPPED    │
       └───────┤ (Hold for 3s) │
               └───────────────┘
```
