# 05. POWER DISTRIBUTION & BUCK CONVERTER CALIBRATION
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Dual-Rail Power Distribution Topology

To prevent microcontroller reset brownouts caused by motor inrush current, the vehicle employs a strict **isolated dual-rail topology**:

```
[ 2S Li-ion Battery: 7.4V - 8.4V ]
       |
  [ SPST Switch ]
       |
       +========================================+
       |                                        |
  (High-Voltage Rail: 7.4V - 8.4V)         (Buck Input)
       |                                        |
  [ TB6612FNG VM Pin ]                     [ LM2596 Buck Converter ]
       |                                        | (Step down to 5.15V DC)
  [ Left / Right TT Motors ]                    |
                                           [ NodeMCU VIN Pin ]
                                                |
                                           [ NodeMCU Onboard LDO (3.3V) ]
                                                |
                                           [ TB6612FNG VCC & Logic Inputs ]
```

### Why This Prevents Brownouts:
When DC gear motors start or stall, they draw up to 1.6A total instantaneous current. If the NodeMCU were powered from the same unfiltered unregulated rail, the battery internal impedance would cause the rail voltage to dip momentarily below 4.5V, causing the ESP8266's internal brownout reset (BOR) circuit to reboot the microcontroller.
The LM2596 buck converter features substantial input and output smoothing capacitors ($220\mu\text{F}$ and $470\mu\text{F}$), maintaining an unwavering 5.15V rail into the NodeMCU's onboard LDO even during aggressive motor acceleration or reversals.

---

## 2. LM2596 Buck Converter Calibration Procedure

> [!WARNING]
> Perform this calibration with a digital multimeter (DMM) **BEFORE** connecting the output wire to the NodeMCU VIN pin! LM2596 modules often ship from the factory adjusted to 12V or maximum voltage, which will immediately destroy the ESP8266 if connected directly.

1. **Disconnect Load:** Ensure the NodeMCU is NOT connected to the LM2596 output screw terminals.
2. **Apply Input Power:** Connect your fully charged 2S Li-ion battery pack (7.4V–8.4V) to `IN+` and `IN-`.
3. **Attach Multimeter:** Set your digital multimeter to DC Volts ($20\text{V}$ range). Touch the red probe to `OUT+` and black probe to `OUT-`.
4. **Adjust Potentiometer:** Using a small precision flathead screwdriver, turn the brass screw on top of the blue cermet potentiometer:
   - Turn **counter-clockwise** (usually 10 to 20 full rotations) until the measured output begins dropping.
   - Fine-tune until the multimeter reads exactly **5.15V DC**.
5. **Why 5.15V?**
   - The NodeMCU has an onboard SPX3819 / AMS1117-3.3 linear regulator with a dropout voltage of $\approx 1.1\text{V}$ to $1.3\text{V}$.
   - Delivering 5.15V ensures the onboard 3.3V LDO operates comfortably in regulation with zero ripple, and compensates for wire resistance voltage drops under Wi-Fi transmission bursts (+19.5 dBm transmit peaks draw ~350 mA).
6. **Lock Adjustment:** Once calibrated to 5.15V, apply a small drop of hot glue or nail polish to the potentiometer screw to prevent vibration from shifting the setting during road runs.
