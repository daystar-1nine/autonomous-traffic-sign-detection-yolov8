#ifndef UDP_PROTOCOL_H
#define UDP_PROTOCOL_H

#include <Arduino.h>
#include <WiFiUdp.h>
#include "motor_driver.h"

struct VehicleCommand {
    String action;
    int speed;
    int trim;
    unsigned long sequence;
    unsigned long timestamp;
    bool valid;
};

class UdpController {
private:
    WiFiUDP udp;
    unsigned int port;
    char buffer[256];
    unsigned long lastSequence;

public:
    UdpController(unsigned int listenPort = 8888) : port(listenPort), lastSequence(0) {}

    void begin() {
        udp.begin(port);
        Serial.printf("[UDP] Listening on Port %u\n", port);
    }

    bool parsePacket(VehicleCommand &cmd) {
        int packetSize = udp.parsePacket();
        if (packetSize <= 0) {
            cmd.valid = false;
            return false;
        }

        int len = udp.read(buffer, 255);
        if (len <= 0) {
            cmd.valid = false;
            return false;
        }
        buffer[len] = 0;
        String msg = String(buffer);
        msg.trim();

        // Protocol Format: "CMD:<ACTION>:<SPEED>:<TRIM>:<SEQ>"
        // Example: "CMD:FORWARD:700:0:1042"
        if (!msg.startsWith("CMD:")) {
            cmd.valid = false;
            return false;
        }

        int p1 = msg.indexOf(':', 4);
        int p2 = (p1 > 0) ? msg.indexOf(':', p1 + 1) : -1;
        int p3 = (p2 > 0) ? msg.indexOf(':', p2 + 1) : -1;

        if (p1 > 0) {
            cmd.action = msg.substring(4, p1);
            if (p2 > 0) {
                cmd.speed = msg.substring(p1 + 1, p2).toInt();
                if (p3 > 0) {
                    cmd.trim = msg.substring(p2 + 1, p3).toInt();
                    cmd.sequence = msg.substring(p3 + 1).toInt();
                } else {
                    cmd.trim = msg.substring(p2 + 1).toInt();
                    cmd.sequence = 0;
                }
            } else {
                cmd.speed = msg.substring(p1 + 1).toInt();
                cmd.trim = 0;
                cmd.sequence = 0;
            }
        } else {
            cmd.action = msg.substring(4);
            cmd.speed = 700;
            cmd.trim = 0;
            cmd.sequence = 0;
        }

        cmd.valid = true;

        // Echo back instantaneous UDP ACK
        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        String ack = "ACK:" + cmd.action + ":" + String(cmd.sequence) + ":" + String(WiFi.RSSI());
        udp.print(ack);
        udp.endPacket();

        return true;
    }
};

#endif // UDP_PROTOCOL_H
