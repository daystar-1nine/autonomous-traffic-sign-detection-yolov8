# 16. WI-FI AP & LOW-LATENCY UDP PROTOCOL
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Network Topology: Standalone SoftAP

The NodeMCU ESP8266 hosts its own dedicated Wi-Fi 802.11 b/g/n SoftAP (Access Point), eliminating the need for an external Wi-Fi router:
- **SSID:** `AutonomousCar_AP`
- **Password:** `car12345678` (or `12345678`)
- **Default IP Address:** `192.168.4.1`
- **Subnet Mask:** `255.255.255.0`
- **UDP Port:** `8888`
- **Web Diagnostic Port:** `80` (Provides `/ping` and `/status` HTTP endpoints)

The Samsung Galaxy A36 5G connects directly to `AutonomousCar_AP`.

---

## 2. Why UDP Over TCP / HTTP?

For autonomous and teleoperated vehicular control, **UDP (User Datagram Protocol)** is vastly superior to TCP and HTTP:

| Dimension | UDP Protocol (Selected) | HTTP / REST API (Rejected) | TCP Stream (Rejected) |
| :--- | :--- | :--- | :--- |
| **Transmission Latency** | **$1.2\text{ ms} - 2.8\text{ ms}$** | $45\text{ ms} - 120\text{ ms}$ | $15\text{ ms} - 35\text{ ms}$ |
| **Head-of-Line Blocking**| **None** (Packets are stateless) | Severe (HTTP connection overhead) | High (Retransmissions freeze pipeline)|
| **Network Overhead** | 8 bytes UDP header | Hundreds of bytes HTTP text headers| 20-60 bytes TCP header |
| **Throughput Frequency** | 30 to 50 Hz sustained | Max 5 to 10 Hz | 20 Hz |

In vehicular robotics, a delayed packet is useless data. The car needs the latest command immediately; discarding a lost packet is preferable to waiting for a TCP retransmission.

---

## 3. Dual-Protocol Packet Specification

The ESP8266 firmware accepts two distinct packet formats on Port 8888:

### Packet Format A: Direct Differential Drive (Manual Mode)
```
CMD:DRIVE:<leftPwm>:<rightPwm>:<sequenceNumber>
```
- `<leftPwm>`: Integer from `-1023` to `+1023` (negative = reverse, positive = forward).
- `<rightPwm>`: Integer from `-1023` to `+1023`.
- `<sequenceNumber>`: Monotonically increasing 32-bit counter for jitter tracking.

Example:
`CMD:DRIVE:750:750:142` -> Drives forward at 75% speed.
`CMD:DRIVE:600:-600:143` -> Performs an in-place pivot right turn.

### Packet Format B: Autonomous Action (Vision Navigation Mode)
```
CMD:<ACTION>:<speed>:<trim>:<sequenceNumber>
```
- Supported Actions: `FORWARD`, `STOP`, `LEFT`, `RIGHT`, `SLOW`, `FAST`.

Example:
`CMD:STOP:0:0:201` -> Triggers emergency hardware active brake.
`CMD:FORWARD:650:0:202` -> Drives forward at calibrated cruising speed.
