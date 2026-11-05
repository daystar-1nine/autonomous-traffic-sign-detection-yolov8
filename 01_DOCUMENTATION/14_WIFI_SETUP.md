# 14 - Wireless Wi-Fi Access Point & Station Configuration

This document explains the two supported wireless networking modes for connecting the **Android Smartphone** to the **ESP8266 Vehicle Controller**.

---

## 📡 Mode 1: Car SoftAP Mode (Default & Recommended)

In this mode, the car acts as its own independent Wi-Fi hotspot. **Zero external routers or mobile hotspots are needed!**

```text
┌─────────────────────────┐               ┌─────────────────────────┐
│     ESP8266 NodeMCU     │  Wi-Fi SoftAP │    Android Smartphone   │
│  SSID: AutonomousCar_AP ├──────────────►│    Connects as Client   │
│    IP: 192.168.4.1      │   (No Router) │    IP: 192.168.4.2      │
└─────────────────────────┘               └─────────────────────────┘
```

### Credentials:
- **SSID:** `AutonomousCar_AP`
- **Password:** `12345678`
- **Car Gateway IP:** `192.168.4.1`
- **UDP Port:** `8888`
- **HTTP Diagnostic Port:** `80`

### How to Connect on Android Phone:
1. Turn ON the car battery switch.
2. On your Redmi phone, open **Settings → Wi-Fi**.
3. Select `AutonomousCar_AP` and enter password `12345678`.
4. If Android displays a prompt *"This network has no internet access. Stay connected?"*, tap **YES / STAY CONNECTED**.

---

## 📶 Mode 2: Station Mode (Phone Mobile Hotspot)

In this mode, the car connects to a mobile hotspot broadcasted by the smartphone.

### How to Enable:
1. In `esp8266_firmware.ino`, change line 20:
   ```cpp
   #define USE_STATION_MODE 1
   const char* STA_SSID     = "Your_Hotspot_Name";
   const char* STA_PASSWORD = "Your_Hotspot_Password";
   ```
2. Re-upload firmware to NodeMCU.
3. Turn on Mobile Hotspot on your phone.
4. The car will connect to your phone and appear in your phone's *Connected Devices* list with an assigned IP address (e.g. `192.168.137.45`).

---

👉 **Next Step:** Proceed to [`15_COMMUNICATION_PROTOCOL.md`](15_COMMUNICATION_PROTOCOL.md) for UDP packet structures.
