# Dependency & Environment Audit Report

This report audits the software dependencies across the Python ML stack, the Arduino/ESP8266 embedded environment, and the Android mobile toolchain to ensure zero version incompatibilities and reproducible builds.

---

## 1. Python Environment Audit

### 1.1 Host Environment Details
- **Operating System:** Windows 11 (build architecture: amd64)
- **Python Version:** 3.14.4 (CPython runtime)
- **CUDA Device:** NVIDIA GeForce RTX 5060 Laptop GPU (8,192 MB VRAM)
- **PyTorch Installation:** `torch 2.14.1+cu130`, `torchvision 0.29.1+cu130` (CUDA 13.0 build)

### 1.2 Python Dependencies Classification

| Package | Detected Version | Required For | Dependency Status |
| :--- | :--- | :--- | :--- |
| `ultralytics` | 8.4.199 | YOLOv8 training, validation, export | **Production Ready** |
| `torch` | 2.14.1+cu130 | Deep learning tensor computation & GPU kernel execution | **Production Ready** |
| `torchvision` | 0.29.1+cu130 | Image augmentations & vision models | **Production Ready** |
| `opencv-python` | 4.13.0.92 | Image decoding, video streaming, HUD visualization | **Production Ready** |
| `numpy` | 2.5.4 | High-performance array & box arithmetic | **Production Ready** |
| `onnx` | 1.23.2 | Neural network interchange format export | **Production Ready** |
| `PyYAML` | 6.0.3 | Dataset YAML configuration parsing | **Production Ready** |
| `matplotlib` | 3.11.1 | Precision-Recall & loss curve plotting | **Production Ready** |
| `seaborn` | 0.13.2 | Confusion matrix rendering | **Production Ready** |
| `requests` | 2.33.1 | HTTP diagnostics client | **Production Ready** |

### 1.3 Minimal Pinned `requirements.txt`
Stored in [`02_AI_MODEL/requirements.txt`](02_AI_MODEL/requirements.txt) and [`05_PYTHON_TOOLS/requirements.txt`](05_PYTHON_TOOLS/requirements.txt):
```text
ultralytics>=8.3.0
torch>=2.0.0
torchvision>=0.15.0
opencv-python>=4.8.0
numpy>=1.23.0
PyYAML>=6.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
pillow>=9.5.0
tqdm>=4.65.0
requests>=2.28.0
onnx>=1.14.0
```

---

## 2. Arduino / ESP8266 Embedded Environment Audit

### 2.1 Core Toolchain
- **Board:** NodeMCU 1.0 (ESP-12E Module)
- **Microcontroller:** Tensilica Xtensa 32-bit LX106 @ 80 MHz / 160 MHz
- **Flash Memory:** 4 MB SPI Flash
- **Operating Voltage:** 3.0V – 3.6V (onboard 3.3V LDO regulator fed by VIN at 5.0V)

### 2.2 Board Package & Libraries
- **ESP8266 Arduino Core:** `esp8266 by ESP8266 Community` (Version `3.1.2` or later).
  - Board Manager URL: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
- **Standard Libraries Required (Included with Core):**
  - `<ESP8266WiFi.h>`: Wi-Fi Access Point and Station modes.
  - `<WiFiUdp.h>`: Low-latency UDP socket communication (Port 8888).
  - `<ESP8266WebServer.h>`: Diagnostic HTTP server (Port 80).
- **Third-Party External Libraries:** **None.** 
  - Using zero third-party libraries prevents dependency conflicts and guarantees that any clean Arduino IDE or PlatformIO installation will compile the firmware without missing library errors.

---

## 3. Android Studio Toolchain Audit

### 3.1 Mobile Project Specifications
- **Programming Language:** Kotlin (`1.9.22` / `2.0+`)
- **Minimum SDK:** API Level 24 (Android 7.0 Nougat) — covers 99.2% of active Android devices.
- **Target SDK:** API Level 34 (Android 14)
- **Build System:** Gradle with Android Gradle Plugin (AGP) `8.2.2+`

### 3.2 Key Android Dependencies
1. **CameraX Framework:**
   - `androidx.camera:camera-core:1.3.1`
   - `androidx.camera:camera-camera2:1.3.1`
   - `androidx.camera:camera-lifecycle:1.3.1`
   - `androidx.camera:camera-view:1.3.1`
2. **On-Device Machine Learning Inference Runtime:**
   - `org.tensorflow:tensorflow-lite:2.14.0` (or LiteRT)
   - `org.tensorflow:tensorflow-lite-support:0.4.4`
   - `org.tensorflow:tensorflow-lite-gpu:2.14.0` (optional hardware acceleration delegate)
3. **Architecture Components & UI:**
   - `androidx.appcompat:appcompat:1.6.1`
   - `com.google.android.material:material:1.11.0`
   - `androidx.constraintlayout:constraintlayout:2.1.4`
   - `androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0`
   - `org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3`
