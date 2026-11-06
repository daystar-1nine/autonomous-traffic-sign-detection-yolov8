# 11 - Wi-Fi UDP Communication Protocol & Heartbeat Specification

---

## 1. Purpose
This document specifies the wireless networking, UDP datagram structure, round-trip acknowledgement, and heartbeat mechanism operating between the Android phone and NodeMCU ESP8266.

---

## 2. Network Topology
- **Wi-Fi Mode:** ESP8266 SoftAP (Access Point).
- **SSID:** `AutonomousCar_AP`.
- **Password:** `car12345678`.
- **Car IP Address:** `192.168.4.1`.
- **Phone IP Address (DHCP):** `192.168.4.2`.
- **UDP Port:** `8888`.
- **Transport Latency:** 1.2ms – 3.2ms.

---

## 3. Packet Wire Formats

### 1. Manual Drive Datagram
```text
CMD:DRIVE:<LEFT_PWM>:<RIGHT_PWM>:<SEQUENCE_NUMBER>\n
```
- `<LEFT_PWM>`: Signed integer $[-1023, 1023]$.
- `<RIGHT_PWM>`: Signed integer $[-1023, 1023]$.
- `<SEQUENCE_NUMBER>`: Monotonically increasing unsigned long.

### 2. Autonomous Action Datagram
```text
CMD:<ACTION>:<SPEED>:<TRIM>:<SEQUENCE_NUMBER>\n
```
- `<ACTION>`: `FORWARD`, `BACKWARD`, `LEFT`, `RIGHT`, `STOP`, `HEARTBEAT`.
- `<SPEED>`: Integer $[0, 1023]$.
- `<TRIM>`: Integer $[-100, 100]$.

### 3. ESP8266 Instantaneous ACK
```text
ACK:<ACTION_OR_DRIVE>:<SEQUENCE_NUMBER>:<RSSI_DBM>
Example: ACK:DRIVE:1042:-42
```

---

## 4. Heartbeat & Watchdog Keep-Alive
- The Android `UdpVehicleClient` runs a dedicated background coroutine on `Dispatchers.IO`.
- Every **200 milliseconds**, if no new movement packet has been dispatched, a heartbeat datagram is transmitted.
- This continuously resets the ESP8266 watchdog timer.
- If the phone Wi-Fi drops or the app is minimized for >1000ms, the ESP8266 watchdog triggers an auto-stop.

---

## 5. Verification Checklist
- [ ] Round-trip UDP latency displays under 5ms on HUD.
- [ ] Packets increment sequence numbers monotonically.
- [ ] ESP8266 echoes ACK with valid RSSI value.
