# 06. BATTERY SELECTION, CHARGING & LI-ION SAFETY
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Battery Pack Configuration & Specifications

The vehicle is engineered to run on a **2S Lithium-Ion Battery Configuration** (two 3.7V nominal 18650 cylindrical cells connected in series):
- **Cell Chemistry:** Lithium Nickel Manganese Cobalt Oxide (NMC) or Lithium Cobalt Oxide (LiCoO2).
- **Nominal Voltage:** $2 \times 3.7\text{V} = \mathbf{7.4\text{V}}$.
- **Full Charge Voltage (Cut-off):** $2 \times 4.20\text{V} = \mathbf{8.40\text{V}}$.
- **Discharge Cut-off Voltage:** $2 \times 3.00\text{V} = \mathbf{6.00\text{V}}$ (Never discharge below 2.8V per cell).
- **Continuous Discharge Rating:** $\ge 5\text{A}$ ($2\text{C}$ minimum for $2500\text{ mAh}$ cells).
- **Usable Energy Capacity:** $\approx 18.5\text{ Wh}$ to $22.2\text{ Wh}$, providing $\approx 90 - 120\text{ minutes}$ of active runtime.

---

## 2. Integrated 2S Battery Management System (BMS)

> [!IMPORTANT]
> Never connect bare 18650 cells without an integrated 2S Protection Circuit Module (BMS). A quality 2S BMS provides four indispensable protection layers:
1. **Overcharge Protection:** Automatically halts charging if any individual cell reaches 4.25V–4.30V.
2. **Over-discharge Protection:** Instantly cuts load current if battery voltage drops below 5.8V–6.0V, preventing permanent chemical degradation and cell death.
3. **Overcurrent & Short-Circuit Protection:** Trips in $<20\text{ ms}$ if motor stall current or wiring short exceeds 8A–10A.
4. **Cell Balancing (Active/Passive):** Equalizes voltage between the two series cells to prevent asymmetric aging.

---

## 3. Safe Charging Guidelines

1. **Use a Dedicated CC/CV 2S Li-ion Smart Charger:**
   - Always charge using a Constant Current / Constant Voltage (CC/CV) charger specifically rated for 8.4V DC output.
   - Recommended charge current: $0.5\text{C}$ to $1.0\text{C}$ (e.g., $1.0\text{A}$ to $1.5\text{A}$ for a $2600\text{ mAh}$ pack).
2. **Never Leave Charging Batteries Unattended:**
   - Charge on a non-flammable surface (e.g., tile, metal tray, or LiPo safety charging bag).
   - Keep away from curtains, paper, and flammable chemicals.
3. **Inspect for Physical Damage Before Every Charge:**
   - Reject any cell showing signs of denting, swelling, wrapper tears, or chemical odor.
   - If a cell feels hot to the touch ($>45^\circ\text{C}$) during charging, disconnect immediately.

---

## 4. Vehicle Low-Voltage Operation Rules

1. When the battery drops below **6.4V** (3.2V per cell), motor torque will noticeably decrease. Stop driving immediately and recharge.
2. Never store the vehicle with a depleted battery pack. If storing for more than 2 weeks, charge to storage voltage ($\approx 3.80\text{V} - 3.85\text{V}$ per cell, or $\approx 7.6\text{V} - 7.7\text{V}$ total pack voltage).
