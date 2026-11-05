# 21 - Frequently Asked Questions (FAQ)

---

### Q1: Why does this car project use a smartphone instead of a Raspberry Pi or Jetson Nano?
**Answer:** Modern Android smartphones (even budget Redmi devices) possess multi-core ARM CPUs, high-speed GPUs, hardware neural NPUs, built-in 1080p camera sensors, rechargeable batteries, and touchscreens. Using the smartphone eliminates the need for expensive onboard computing boards ($150–$300 for Jetson) while providing higher inference framerates with lower weight.

---

### Q2: Why are the STOP signs in this project BLUE instead of RED?
**Answer:** The dataset (`Traffic-Signs-new`) is based on international embedded autonomous vehicle benchmarks (such as the FIRA autonomous simulation challenge), where regulatory and track signs use high-contrast blue disc and octagonal backgrounds with white iconography. The model detects these signs with **99.5% accuracy**. Standard red US/European stop signs from Google Images belong to a different distribution.

---

### Q3: Why is TB6612FNG used instead of L298N?
**Answer:** The L298N is based on obsolete BJT (bipolar junction transistor) silicon technology from the 1980s. It drops approximately 2.0V to 2.5V as waste heat! When using a 7.4V battery with an L298N, your motors only receive ~5.0V, resulting in sluggish performance. The TB6612FNG uses modern MOSFETs with low on-resistance ($0.5\,\Omega$), delivering almost the full 7.4V directly to the motors with virtually zero heat.

---

### Q4: Does the car require an active internet connection to run?
**Answer:** **No.** The entire system is 100% self-contained and local. The ESP8266 generates its own private local Wi-Fi Access Point (`AutonomousCar_AP`), and all neural network inference runs entirely on the smartphone's internal processor using TensorFlow Lite.

---

### Q5: Can I use this code with an external laptop instead of the phone?
**Answer:** **Yes.** The desktop simulation tool [`05_PYTHON_TOOLS/scripts/pc_telemetry_hud.py`](../05_PYTHON_TOOLS/scripts/pc_telemetry_hud.py) implements the identical UDP command protocol and state machine logic. You can stream video from your phone or webcam to your laptop and control the car wirelessly over Wi-Fi during laboratory testing.

---

👉 **Next Step:** Proceed to [`22_FINAL_CHECKLIST.md`](22_FINAL_CHECKLIST.md) for the pre-flight sign-off checklist.
