#ifndef WATCHDOG_H
#define WATCHDOG_H

#include <Arduino.h>
#include "motor_driver.h"

class SafetyWatchdog {
private:
    unsigned long lastHeartbeat;
    unsigned long timeoutMs;
    bool triggered;

public:
    SafetyWatchdog(unsigned long timeout = 1000) 
        : lastHeartbeat(0), timeoutMs(timeout), triggered(false) {}

    void feed() {
        lastHeartbeat = millis();
        triggered = false;
    }

    void check(MotorDriver &motors) {
        if (!triggered && motors.currentAction != "STOP") {
            if (millis() - lastHeartbeat > timeoutMs) {
                Serial.println("[WATCHDOG] Communication lease expired! Auto-stopping motors.");
                motors.stop();
                triggered = true;
            }
        }
    }

    bool isTimedOut() const {
        return triggered;
    }
};

#endif // WATCHDOG_H
