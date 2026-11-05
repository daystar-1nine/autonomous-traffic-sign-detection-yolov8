# 16 - Autonomous Driving & Decision Engine Operation

This document explains the autonomous decision-making pipeline, state machine transitions, and sign reaction logic in the **AI Autonomous Car**.

---

## 🧠 Decision Engine Pipeline

The decision engine strictly decouples raw neural network detections from motor actuation through a 6-stage verification sequence:

```text
Camera Frame (30 FPS)
       │
       ▼
[Stage 1: YOLOv8n Inference] ──► Generates candidate bounding boxes [x, y, w, h, class, conf]
       │
       ▼
[Stage 2: Confidence Filter] ──► Rejects detections where confidence < 0.60
       │
       ▼
[Stage 3: Geometric Filter] ───► Verifies aspect ratio (0.45 <= W/H <= 2.2) and screen area
       │
       ▼
[Stage 4: Temporal Debounce] ──► Confirms candidate seen in >= 2 consecutive frames
       │
       ▼
[Stage 5: Proximity Zone] ────► Evaluates distance based on bounding box height ratio
       │
       ▼
[Stage 6: State Machine] ─────► Executes Maneuver (Cruise, Approach, Turn, Hold Stop)
       │
       ▼
[UDP Dispatch to ESP8266]
```

---

## 🎯 Supported Traffic Signs & Autonomous Behaviors

The system supports the **6 actual classes** in the trained model:

| Sign Name | Visual Icon | Proximity Trigger | Autonomous Behavior |
| :--- | :---: | :---: | :--- |
| **`straight_ahead`** | ⬆️ | Any distance | Maintains standard cruising speed (PWM 700). Path is confirmed clear. |
| **`stop`** | 🛑 | Height $\ge 11\%$ (Action Zone) | Complete halt at the stop line. Engages regenerative brake and **holds position for 3.0 seconds**, then safely resumes cruising once intersection is clear. |
| **`stop` (Approach)** | 🛑 | $6\% \le \text{Height} < 11\%$ | **Smooth Deceleration**: Dynamically ramps down PWM from 700 to 480 to prepare for stop line. |
| **`left_turn`** | ⬅️ | Height $\ge 11\%$ (Action Zone) | **Maneuver Lock**: Enters TURNING state and executes calibrated differential left turn for **0.85 seconds**, then realigns straight and enters a **2.5s cooldown** against duplicate turns. |
| **`right_turn`** | ➡️ | Height $\ge 11\%$ (Action Zone) | **Maneuver Lock**: Enters TURNING state and executes calibrated differential right turn for **0.85 seconds**, then realigns straight and enters a **2.5s cooldown**. |
| **`dead_end`** | ⛔ | Height $\ge 10\%$ | Halts vehicle before track boundary; initiates safe turnaround or holds stop. |
| **`no_entry`** | ⛔ | Height $\ge 10\%$ | Immediate safety brake. Prohibits forward traversal into forbidden sector. |

---

## ⏱️ Cooldown & Duplicate Turn Prevention

- **Problem:** When an autonomous car turns left at an intersection, the left sign may briefly remain in the corner of the camera frame. A naive controller would see the sign again and trigger a second turn, spinning in circles!
- **Engineering Solution:** After completing a turn, the Decision Engine engages a **2.5-second cooldown timer**. During cooldown, duplicate turning signs are suppressed while the car cruises straight ahead, allowing the vehicle to clear the intersection.

---

👉 **Next Step:** Proceed to [`17_MANUAL_MODE.md`](17_MANUAL_MODE.md) to inspect manual override features.
