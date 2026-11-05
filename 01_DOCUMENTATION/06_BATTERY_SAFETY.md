# 06 - Lithium-Ion Battery Safety & Protection Guide

This document defines mandatory safety rules, storage protocols, and fuse protection requirements for the **18650 Lithium-ion Battery Pack** powering the autonomous vehicle.

---

## ⚠️ Critical Battery Safety Protocols

> [!CAUTION]
> **Lithium-Ion Fire Hazard**: 18650 Li-ion cells contain significant chemical energy. Short circuits, physical punctures, overcharging, or over-discharging can cause thermal runaway, venting, or fire. Adhere strictly to the guidelines below.

### 1. Voltage Boundaries (Per 3.7V Cell)
- **Maximum Safe Voltage (Full Charge):** **4.20 V** (Never exceed 4.25 V).
- **Nominal Operating Voltage:** **3.60 V – 3.70 V**.
- **Minimum Safe Cutoff Voltage:** **3.00 V** (Never discharge below 2.70 V).
- **Total 2S Pack Cutoff:** If total pack voltage drops below **6.0 V**, disconnect immediately and recharge.

### 2. Physical Battery Inspection Checklist
- [ ] Inspect outer heat-shrink PVC wrapper. If torn, re-wrap before installing in car.
- [ ] Verify positive terminal insulator ring is intact.
- [ ] Check for dents, punctures, or chemical leakage. Discard damaged cells safely.
- [ ] Ensure springs in battery holder make firm contact without bending cell terminals.

---

## 🛡️ Over-Current & Fuse Protection

```text
  [Battery +] ───► [ 3A Fast-Blow Inline Fuse ] ───► [ Power Switch ] ───► System
```

- **Fuse Rating:** **3.0 A Fast-Blow (5x20mm glass or automotive blade fuse)**.
- **Justification:** Total nominal running current is $\approx 0.53\text{ A}$. Dual motor stall current peaks at $\approx 2.4\text{ A}$. A 3.0A fuse allows motor starting surges while blowing instantly if a catastrophic short-circuit occurs across battery leads.

---

## ⚡ Charging & Storage Guidelines

1. **Approved Chargers Only:** Use a dedicated CC/CV (Constant Current / Constant Voltage) Lithium-ion balance charger. Never use unregulated DC wall adapters.
2. **Attended Charging:** Always charge batteries on a non-flammable surface (e.g. ceramic tile or LiPo safety bag). Never leave charging cells unattended overnight.
3. **Long-Term Storage Voltage:** If the robot car is stored unused for more than two weeks, discharge/charge cells to **3.80V – 3.85V per cell (7.6V–7.7V total pack)**.

---

👉 **Next Step:** Proceed to [`07_SOFTWARE_INSTALLATION.md`](07_SOFTWARE_INSTALLATION.md) to set up development environments.
