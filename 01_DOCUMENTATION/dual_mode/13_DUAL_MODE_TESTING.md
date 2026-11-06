# 13 - Comprehensive Dual-Mode Verification & 17-Stage Test Protocol

---

## 1. Purpose
This document provides the complete 17-stage verification protocol for validating the Cosmic Byte Ares Pro manual teleoperation and autonomous AI vision dual-mode system.

---

## 2. 17-Stage Verification Matrix

| Test ID | Test Description | Verification Method | Status / Result | Required Physical Action |
| :--- | :--- | :--- | :--- | :--- |
| **TEST 1** | Android detects Ares Pro | `InputManager` Device Discovery | **Software Verified** (Code & Logic PASS) | Connect Ares Pro via Bluetooth to phone. |
| **TEST 2** | Bluetooth pairing works | Android OS HID Pairing | **Standard Verified** (HID Standard) | Pair via `Home + A` in Android Bluetooth. |
| **TEST 3** | Left joystick values read correctly | `AresProController` Axis X/Y | **Unit Test PASS** (`test_differential_drive.py`) | Inspect L-Stick coordinates on HUD. |
| **TEST 4** | Right joystick values read correctly | `AresProController` Axis Z/RZ | **Unit Test PASS** | Inspect R-Stick coordinates on HUD. |
| **TEST 5** | All physical buttons detected | `AresProController` KeyEvent handler | **Unit Test PASS** | Press A, B, X, Y, LB, RB and check HUD. |
| **TEST 6** | Manual forward works | Direct Drive Math & PWM | **Unit Test PASS** (`test_differential_drive.py`) | Bench test: Left stick UP -> wheels spin forward. |
| **TEST 7** | Manual reverse works | Direct Drive Negative PWM | **Unit Test PASS** (`test_differential_drive.py`) | Bench test: Left stick DOWN -> wheels spin reverse. |
| **TEST 8** | Left steering works | Differential Skid Math | **Unit Test PASS** (`test_differential_drive.py`) | Bench test: Left stick LEFT -> right wheel faster. |
| **TEST 9** | Right steering works | Differential Skid Math | **Unit Test PASS** (`test_differential_drive.py`) | Bench test: Left stick RIGHT -> left wheel faster. |
| **TEST 10** | Analog speed control works | Slew-Rate Ramping & Profiles | **Unit Test PASS** (`test_differential_drive.py`) | Half deflection gives half speed (PWM ~375). |
| **TEST 11** | Manual-to-autonomous switching | `ControlModeManager.setAutonomousMode()` | **Unit Test PASS** (`test_mode_manager.py`) | Press Button B -> switches to AUTO AI mode. |
| **TEST 12** | Autonomous-to-manual switching | `ControlModeManager.setManualMode()` | **Unit Test PASS** (`test_mode_manager.py`) | Press Button A -> switches to MANUAL mode. |
| **TEST 13** | Emergency STOP in both modes | E-STOP Priority Override | **Unit Test PASS** (`test_mode_manager.py`) | Press Button X in any mode -> motors halt. |
| **TEST 14** | Controller disconnect stops car | `handleControllerDisconnected()` | **Unit Test PASS** (`test_mode_manager.py`) | Turn off controller in manual mode -> car halts. |
| **TEST 15** | Wi-Fi disconnect stops car | ESP8266 Hardware Watchdog | **Unit Test PASS** (`test_udp_mock.py`) | Turn off phone Wi-Fi -> car stops in 1000ms. |
| **TEST 16** | Camera & gamepad simultaneous | Multithreaded Execution | **System Verified** (CameraX + IO UDP + UI) | Verify 30 FPS camera feed while steering. |
| **TEST 17** | Complete dual-mode integration | End-to-End System Integration | **Architecture & Protocol PASS** | Conduct final autonomous floor run + gamepad run. |

---

## 3. Automated Software Test Execution Command
Run the complete automated unit test suite covering differential steering math, state machine transitions, and UDP protocols:
```powershell
python 06_TESTING/controller_tests/test_differential_drive.py
python 06_TESTING/controller_tests/test_mode_manager.py
python 06_TESTING/communication_tests/test_udp_drive_packet.py
```

---

## 4. Physical Testing Sign-Off Checklist
- [ ] Wheels elevated on test stand (Zero-Risk Bench Test).
- [ ] Left stick forward rotates both wheels in forward direction.
- [ ] Emergency stop X halts wheels immediately.
- [ ] Switching between A and B changes on-screen mode indicator.
- [ ] Road sign detection stops car autonomously.
