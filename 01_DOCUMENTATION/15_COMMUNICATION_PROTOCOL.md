# 15 - Real-Time Wireless UDP Protocol Specification

This document defines the high-speed **UDP Datagram Protocol** operating on **Port 8888** between the Android Vision Brain and the ESP8266 Vehicle Controller.

---

## ⚡ Protocol Architecture: Why UDP over HTTP?

| Metric | HTTP REST (TCP) | UDP Datagrams (This Protocol) |
| :--- | :--- | :--- |
| **Connection Overhead** | 3-way TCP handshake + HTTP headers | **Zero handshake (Connectionless)** |
| **Transmission Latency** | 35 ms – 200 ms (head-of-line blocking) | **1.2 ms – 3.5 ms** |
| **Packet Loss Behavior** | Blocks stream waiting for retransmission | **Drops stale packet; newest frame acts immediately** |
| **CPU Usage on ESP8266** | High (String allocs & HTTP parser) | **Minimal (Fixed-size byte buffer parse)** |

---

## 📦 Packet Structure & Syntax

All packets are plain-text ASCII datagrams terminated by a newline (`\n`).

### 1. Command Packet (Android $\rightarrow$ ESP8266)
```text
CMD:<ACTION>:<SPEED>:<TRIM>:<SEQUENCE_NUM>
```

#### Fields:
1. `CMD:` - Fixed 4-byte header identifier.
2. `<ACTION>` - Vehicle navigation action:
   - `FORWARD` : Dual motors drive forward.
   - `BACKWARD` : Dual motors reverse.
   - `LEFT` : Differential skid turn left.
   - `RIGHT` : Differential skid turn right.
   - `STOP` : Immediate zero-speed brake.
   - `HEARTBEAT`: Null action to refresh watchdog lease.
3. `<SPEED>` - Motor PWM duty cycle: Integer `0` to `1023`.
4. `<TRIM>` - Motor balance trim: Integer `-100` to `+100` (Negative = slows left motor, Positive = slows right motor).
5. `<SEQUENCE_NUM>` - Monotonically increasing unsigned long packet counter.

#### Examples:
```text
CMD:FORWARD:700:0:1042\n
CMD:LEFT:760:0:1043\n
CMD:STOP:0:0:1044\n
```

---

### 2. Acknowledgment Packet (ESP8266 $\rightarrow$ Android)
```text
ACK:<CURRENT_ACTION>:<SEQUENCE_NUM>:<WIFI_RSSI>
```

#### Example:
```text
ACK:FORWARD:1042:-48\n
```

---

## ⏱️ Watchdog Timer & Control Lease

- **Lease Period:** **1,000 ms (1.0 second)**.
- **Heartbeat Rate:** The Android app sends a command or heartbeat packet every **200 ms**.
- **Fail-Safe Behavior:** If the phone camera closes, the app crashes, or the car drives out of Wi-Fi range for $>1,000\text{ ms}$, the ESP8266 automatically shuts off all motor PWM signals.

---

👉 **Next Step:** Proceed to [`16_AUTONOMOUS_MODE.md`](16_AUTONOMOUS_MODE.md) to understand autonomous driving states.
