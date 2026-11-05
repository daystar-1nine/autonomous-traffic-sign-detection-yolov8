# 08 - Python Environment & Dependencies Setup

This document provides exact commands to set up an isolated virtual environment and install all dependencies for training, validation, export, and diagnostics.

---

## 💻 Virtual Environment Creation (Windows PowerShell)

Open Windows PowerShell in the project directory:

```powershell
# 1. Navigate to workspace
cd "S:\Kaushalya 2.0\R with CV"

# 2. Create isolated virtual environment named 'venv'
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# (If PowerShell blocks script execution, run this once:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)
```

---

## 📦 Dependency Installation

With `(venv)` active in your terminal prompt:

```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all project dependencies
pip install -r 02_AI_MODEL/requirements.txt
```

### PyTorch with CUDA Acceleration (Optional for local NVIDIA GPU training):
If you have an NVIDIA GPU (e.g. RTX 3050, 4060, 5060):
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

## ✅ Verification Checklist

Run this one-line command to verify that all modules load properly:

```powershell
python -c "import torch, ultralytics, cv2, onnx; print('All core libraries verified successfully! PyTorch CUDA Available:', torch.cuda.is_available())"
```

Expected output:
```text
All core libraries verified successfully! PyTorch CUDA Available: True (or False if CPU)
```

---

👉 **Next Step:** Proceed to [`09_MODEL_TRAINING.md`](09_MODEL_TRAINING.md) to train or inspect the YOLOv8 model.
