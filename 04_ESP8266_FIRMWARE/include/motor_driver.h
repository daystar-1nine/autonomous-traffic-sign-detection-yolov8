#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

#include <Arduino.h>
#include "pin_config.h"

class MotorDriver {
public:
    int currentSpeed;
    int targetSpeed;
    int motorTrim; // -100 to +100
    String currentAction;

    MotorDriver() : currentSpeed(0), targetSpeed(700), motorTrim(0), currentAction("STOP") {}

    void init() {
        pinMode(PIN_PWMA, OUTPUT);
        pinMode(PIN_AIN1, OUTPUT);
        pinMode(PIN_AIN2, OUTPUT);
        pinMode(PIN_BIN1, OUTPUT);
        pinMode(PIN_BIN2, OUTPUT);
        pinMode(PIN_PWMB, OUTPUT);
        pinMode(PIN_STBY, OUTPUT);
        pinMode(PIN_LED, OUTPUT);

        // Set PWM Frequency to smooth 1000 Hz
        analogWriteFreq(1000);

        // Keep Standby HIGH so driver is enabled
        digitalWrite(PIN_STBY, HIGH);
        stop();
    }

    void setTrim(int trim) {
        motorTrim = constrain(trim, -100, 100);
    }

    void stop() {
        analogWrite(PIN_PWMA, 0);
        analogWrite(PIN_PWMB, 0);
        digitalWrite(PIN_AIN1, LOW);
        digitalWrite(PIN_AIN2, LOW);
        digitalWrite(PIN_BIN1, LOW);
        digitalWrite(PIN_BIN2, LOW);
        currentSpeed = 0;
        currentAction = "STOP";
        digitalWrite(PIN_LED, HIGH); // LED OFF (Active LOW)
    }

    void forward(int speed) {
        targetSpeed = constrain(speed, 0, 1023);
        applyDirectMotors(targetSpeed, true, targetSpeed, true);
        currentAction = "FORWARD";
        digitalWrite(PIN_LED, LOW); // LED ON
    }

    void backward(int speed) {
        targetSpeed = constrain(speed, 0, 1023);
        applyDirectMotors(targetSpeed, false, targetSpeed, false);
        currentAction = "BACKWARD";
    }

    void turnLeft(int speed) {
        targetSpeed = constrain(speed, 0, 1023);
        // Differential Skid Turn: Left motor reverse, Right motor forward
        applyDirectMotors(targetSpeed / 2, false, targetSpeed, true);
        currentAction = "LEFT";
    }

    void turnRight(int speed) {
        targetSpeed = constrain(speed, 0, 1023);
        // Differential Skid Turn: Left motor forward, Right motor reverse
        applyDirectMotors(targetSpeed, true, targetSpeed / 2, false);
        currentAction = "RIGHT";
    }

private:
    void applyDirectMotors(int leftSpeed, bool leftFwd, int rightSpeed, bool rightFwd) {
        // Compensate with motorTrim
        int adjLeft = leftSpeed;
        int adjRight = rightSpeed;

        if (motorTrim < 0) {
            adjLeft = adjLeft + (adjLeft * motorTrim / 200);
        } else if (motorTrim > 0) {
            adjRight = adjRight - (adjRight * motorTrim / 200);
        }

        adjLeft = constrain(adjLeft, 0, 1023);
        adjRight = constrain(adjRight, 0, 1023);

        // Left Motor (A)
        digitalWrite(PIN_AIN1, leftFwd ? HIGH : LOW);
        digitalWrite(PIN_AIN2, leftFwd ? LOW : HIGH);
        analogWrite(PIN_PWMA, adjLeft);

        // Right Motor (B)
        digitalWrite(PIN_BIN1, rightFwd ? HIGH : LOW);
        digitalWrite(PIN_BIN2, rightFwd ? LOW : HIGH);
        analogWrite(PIN_PWMB, adjRight);

        currentSpeed = (adjLeft + adjRight) / 2;
    }
};

#endif // MOTOR_DRIVER_H
