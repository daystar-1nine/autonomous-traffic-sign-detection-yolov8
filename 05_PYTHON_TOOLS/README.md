# Python Development & Diagnostic Toolchain

This directory houses the development, validation, diagnostic, and desktop simulation suite for the **Autonomous AI Car Project**.

---

## 🛠️ Included Tools

| Script | Purpose | Usage Command |
| :--- | :--- | :--- |
| `validate_dataset.py` | Audits dataset integrity, coordinates, MD5 duplicate images | `python 05_PYTHON_TOOLS/scripts/validate_dataset.py --data-dir dataset` |
| `compare_models.py` | Compares YOLOv8n vs YOLOv8s parameters, GFLOPs, latency | `python 05_PYTHON_TOOLS/scripts/compare_models.py` |
| `test_communication.py` | Sends UDP & HTTP ping packets to ESP8266 and measures latency | `python 05_PYTHON_TOOLS/scripts/test_communication.py --esp-ip 192.168.4.1` |
| `test_detection.py` | Tests sign detection with false-positive filtering on sample images | `python 05_PYTHON_TOOLS/scripts/test_detection.py --source dataset/sample_signs` |
| `test_camera.py` | Verifies camera devices, framerate, and hardware privacy shutter | `python 05_PYTHON_TOOLS/scripts/test_camera.py --index 0` |
| `pc_telemetry_hud.py` | Desktop vehicle cockpit HUD simulator for PC prototyping | `python 05_PYTHON_TOOLS/scripts/pc_telemetry_hud.py --stream-url <url> --esp-ip 192.168.4.1` |

---

## 🚀 Environment Setup

```bash
cd "S:/Kaushalya 2.0/R with CV"
pip install -r 05_PYTHON_TOOLS/requirements.txt
```
