# 19 - Step-by-Step System Testing & Validation Guide

This document provides a structured testing protocol to validate each subsystem independently before proceeding to full autonomous track driving.

---

## 🧪 Phase 1: Benchtop Component Testing (Elevated Wheels)

Always perform initial motor and communication tests with the vehicle chassis supported on a block so the drive wheels spin freely in the air.

### Test 1.1: Standalone Motor Direction Check
1. Power on car via battery switch.
2. In PowerShell, run the communication tool:
   ```powershell
   python "05_PYTHON_TOOLS/scripts/test_communication.py" --esp-ip 192.168.4.1
   ```
3. Send forward command:
   ```text
   CMD:FORWARD:700:0:1
   ```
4. Verify both left and right wheels rotate in the **forward** direction.
   - If a wheel rotates backward, swap its motor wires on TB6612FNG (`AO1/AO2` for Left, `BO1/BO2` for Right).

### Test 1.2: Fail-Safe Watchdog Verification
1. Send forward command: `CMD:FORWARD:700:0:1`.
2. Do not send any further commands.
3. Observe wheels: within **1.0 second**, the ESP8266 watchdog must expire and halt both wheels automatically.
4. If wheels continue spinning after 1.5 seconds, re-check watchdog timeout logic in `esp8266_firmware.ino`.

---

## 🧪 Phase 2: Computer Vision & AI Validation

### Test 2.1: Model Loading & Test Image Verification
Run the automated model inference unit test:
```powershell
python "06_TESTING/model_tests/test_model_inference.py"
```
Expected output:
```text
 [PASS] Model instantiated and inference executed on dummy frame.
 [PASS] Sample stop sign correctly detected with confidence: 95.24%
ALL MODEL TESTS PASSED!
```

### Test 2.2: Decision State Machine Integration Test
Run the decision engine integration unit test:
```powershell
python "06_TESTING/integration_tests/test_decision_engine.py"
```
Expected output:
```text
 [PASS] Single frame blip rejected by debounce filter.
 [PASS] Two consecutive frames confirmed STOP maneuver.
 [PASS] Manual override successfully forced STOP command.
ALL DECISION ENGINE TESTS PASSED!
```

---

## 🧪 Phase 3: Full Autonomous Floor Track Test

1. Print or display the 6 sample traffic signs from [`dataset/sample_signs/`](../dataset/sample_signs/):
   - `sample_5_stop.jpg` (Blue STOP octagon)
   - `sample_0_left_turn.jpg` (Blue left arrow)
   - `sample_2_right_turn.jpg` (Blue right arrow)
2. Place signs on card stock along your floor test course.
3. Place the car 2 meters in front of a STOP sign.
4. Mount the smartphone, open the Android app, and verify the sign is enclosed in a bounding box.
5. Tap **AUTO MODE**:
   - The car moves forward at cruise speed.
   - As it gets closer ($1.0\text{m} \rightarrow 0.5\text{m}$), it smoothly decelerates.
   - When entering the Action Zone, it comes to a complete halt and holds for 3.0 seconds.
6. Verify emergency stop: Tap **EMERGENCY STOP** on the phone screen at any time; the car must stop instantly.

---

👉 **Next Step:** Proceed to [`20_TROUBLESHOOTING.md`](20_TROUBLESHOOTING.md) if any step produces unexpected results.
