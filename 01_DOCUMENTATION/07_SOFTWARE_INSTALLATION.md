# 07 - Clean Software Toolchain Installation Guide

This document guides you through installing all required software tools from zero on a fresh Windows development machine.

---

## 🛠️ Required Software Inventory

| Software Package | Recommended Version | Download Source | Purpose |
| :--- | :---: | :--- | :--- |
| **Python** | 3.10, 3.11, or 3.12+ | [python.org](https://www.python.org/downloads/) | AI training, evaluation, export & PC tools |
| **Git for Windows** | 2.40+ | [git-scm.com](https://git-scm.com/download/win) | Version control & repository synchronization |
| **VS Code** | Latest Stable | [code.visualstudio.com](https://code.visualstudio.com/) | Code editor & terminal workspace |
| **Arduino IDE** | 2.2.1+ or 1.8.19 | [arduino.cc/software](https://www.arduino.cc/en/software) | Compiling and uploading ESP8266 firmware |
| **Android Studio** | Hedgehog / Iguana / Koala | [developer.android.com/studio](https://developer.android.com/studio) | Building and deploying the Kotlin vision app |

---

## 💻 Step-by-Step Installation Instructions

### 1. Python Installation
1. Download the Windows installer from `python.org`.
2. **CRITICAL CHECKBOX:** At the bottom of the first setup screen, check **"Add python.exe to PATH"**.
3. Click **Install Now**.
4. Open Windows PowerShell and verify:
   ```powershell
   python --version
   pip --version
   ```

### 2. Git Installation
1. Run the Git installer, accepting standard defaults.
2. Verify in PowerShell:
   ```powershell
   git --version
   ```

### 3. Arduino IDE & ESP8266 Core Setup
1. Install Arduino IDE.
2. Go to **File → Preferences**.
3. In **Additional Board Manager URLs**, paste:
   ```text
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
4. Click **OK**.
5. Open **Tools → Board → Boards Manager**, search for `ESP8266`, and click **Install**.

### 4. Android Studio Setup
1. Run the Android Studio installer.
2. Select standard installation (includes Android SDK, Android SDK Platform-Tools, and Build-Tools).
3. Open **SDK Manager** (gear icon) and verify **Android 14.0 (API 34)** or **Android 13.0 (API 33)** is checked.

---

👉 **Next Step:** Proceed to [`08_PYTHON_SETUP.md`](08_PYTHON_SETUP.md) to set up your Python environment.
