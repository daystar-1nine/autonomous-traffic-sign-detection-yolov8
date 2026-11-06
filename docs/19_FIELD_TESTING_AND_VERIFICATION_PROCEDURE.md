# 19. FIELD TESTING & VEHICLE VERIFICATION PROCEDURE
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Pre-Flight Vehicle Checklist

Before powering on the vehicle for outdoor or hallway track runs:

- [ ] **Mechanical Inspection:** Both drive wheels securely mounted to motor shafts; front caster wheel rotates freely 360 degrees.
- [ ] **Smartphone Mount:** Phone clamp tightened firmly with rear camera unobstructed and leveled with the road.
- [ ] **Battery Voltage Check:** 2S Li-ion pack measures $\ge 7.6\text{V}$ (never start runs under 7.0V).
- [ ] **Buck Converter Output:** Multimeter confirms LM2596 delivers $5.15\text{V} \pm 0.05\text{V}$ to NodeMCU VIN.
- [ ] **Controller Battery:** Cosmic Byte Ares Pro battery charged (LED indicators solid).
- [ ] **Wi-Fi AP Connection:** Samsung Galaxy A36 5G connected to `AutonomousCar_AP` (`192.168.4.1`).

---

## 2. Test Phase 1: Manual Teleoperation & Failsafe Verification

1. **Power-On Test:**
   - Flip the chassis power switch to ON.
   - Verify NodeMCU power LED lights up and TB6612FNG does not heat up.
   - Launch the Android App. Confirm UDP connection status indicates `CONNECTED (192.168.4.1:8888)`.
2. **Controller Pairing & Mode Engagement:**
   - Turn on Cosmic Byte Ares Pro. Verify Bluetooth pairing to Samsung A36 5G.
   - Press **Button A** on the controller. Confirm Cockpit HUD updates to `MODE: MANUAL`.
3. **Motion Range Test:**
   - Gently push left thumbstick forward. Confirm both wheels rotate forward smoothly without jerking.
   - Pull thumbstick back. Confirm reverse rotation.
   - Deflect stick left/right. Confirm differential wheel speeds.
4. **Emergency Stop Preemption Test:**
   - While driving forward at normal speed, press **Button X** (Emergency Stop).
   - Verify car halts within $<150\text{ ms}$ with active braking.
5. **Controller Disconnect Failsafe Test:**
   - While driving forward, power off the Ares Pro gamepad.
   - Verify car immediately halts and enters locked Emergency Stop state.

---

## 3. Test Phase 2: Autonomous Traffic Sign Detection & Navigation

1. **Test Track Layout:**
   - Set up an indoor test track or smooth corridor with standard miniature traffic signs placed along the course.
   - Sign 1 (Distance 2.0m): `straight_ahead`
   - Sign 2 (Distance 1.5m): `left_turn`
   - Sign 3 (Distance 1.0m): `stop`
2. **Engage Autonomous Mode:**
   - Tap **AUTONOMOUS** on the Android HUD or press **Button B** on the controller.
3. **Observation & Logging:**
   - Verify Cockpit HUD draws green bounding box around detected signs.
   - Confirm confidence score $\ge 0.70$.
   - Confirm car drives forward upon detecting `straight_ahead`.
   - Confirm car steers left smoothly upon reaching `left_turn`.
   - Confirm car halts and holds brake for 3 seconds upon reaching `stop`.
