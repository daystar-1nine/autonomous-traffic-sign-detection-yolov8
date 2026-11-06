# 08. PYTHON DEVELOPMENT ENVIRONMENT SETUP
**Autonomous AI Traffic Sign Detection Car**

---

## 1. Python Environment Prerequisites

The Python tools and machine learning scripts require **Python 3.10 to 3.14 (64-bit)** on Windows, Linux, or macOS.

### Recommended Environment Isolation
Always use a Python virtual environment to prevent package version conflicts with global libraries:

```bash
# Navigate to the project root
cd "s:\Kaushalya 2.0\R with CV"

# Create a virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate
```

---

## 2. Core Dependencies & Installation

Install the required production packages specified in `requirements.txt`:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Key Libraries & Roles:

| Library | Version Requirement | Operational Purpose |
| :--- | :--- | :--- |
| **`ultralytics`** | $\ge 8.3.0$ | YOLOv8 neural network architecture, training, evaluation, anchor-free heads |
| **`torch` & `torchvision`** | $\ge 2.0.0$ | PyTorch tensor acceleration (CUDA GPU or CPU ARM NEON) |
| **`opencv-python`** | $\ge 4.8.0$ | Real-time video frame capture, color normalization, drawing bounding boxes |
| **`numpy`** | $\ge 1.23.0$ | High-speed array operations, tensor dimension slicing, IoU math |
| **`onnx`** | $\ge 1.14.0$ | Open Neural Network Exchange parsing, model metadata inspection |
| **`Pillow`** | $\ge 9.5.0$ | High-speed JPEG/PNG header parsing in dataset conversion tools |
| **`PyYAML`** | $\ge 6.0.0$ | Dataset configuration parsing (`data.yaml`) |
| **`matplotlib` & `seaborn`** | $\ge 3.7.0$ | Generating confusion matrices, Precision-Recall curves, F1 curves |

---

## 3. Environment Verification Command

Verify that your Python environment is configured correctly:

```bash
python -c "
import torch, ultralytics, cv2, numpy, onnx
print('PyTorch Version:', torch.__version__)
print('CUDA Available:', torch.cuda.is_available())
print('Ultralytics Version:', ultralytics.__version__)
print('OpenCV Version:', cv2.__version__)
print('ONNX Version:', onnx.__version__)
print('[OK] Machine learning environment is fully operational.')
"
```
