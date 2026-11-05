# 11 - Android Studio & Device Developer Setup

This document prepares your Android development environment and configures your **Redmi smartphone** for direct APK sideloading and debugging.

---

## 📱 Preparing the Redmi Android Smartphone

To allow Android Studio to deploy and debug apps on your Redmi phone:

### 1. Enable Developer Options
1. Open **Settings** on your Redmi phone.
2. Navigate to **About phone**.
3. Tap repeatedly (7 times) on **OS Version** or **MIUI version** until a toast message says:
   > *"You are now a developer!"*

### 2. Enable USB Debugging
1. Go back to **Settings → Additional settings → Developer options**.
2. Enable **Developer options** (toggle ON).
3. Scroll down and enable **USB debugging**.
4. Enable **Install via USB**.
5. Enable **USB debugging (Security settings)** if prompted by MIUI/HyperOS (requires SIM card active or tap accept 3 times).

---

## 🛠️ Configuring Android Studio

1. Launch Android Studio.
2. Select **Open** and choose the project directory:
   ```text
   S:\Kaushalya 2.0\R with CV\03_ANDROID_APP
   ```
3. Allow Gradle to download required build tools and libraries.
4. Verify Android SDK settings:
   - Go to **Tools → SDK Manager**.
   - Under **SDK Platforms**, ensure **Android 14.0 ("UpsideDownCake") - API 34** or **Android 13.0 - API 33** is installed.
   - Under **SDK Tools**, ensure **Android SDK Build-Tools**, **Android SDK Command-line Tools**, and **Android SDK Platform-Tools** are installed.

---

## 🔌 Connecting Device via USB

1. Connect the Redmi phone to your PC via a high-quality USB-C data cable.
2. When the phone prompts *"Allow USB debugging from this computer?"*, check **Always allow from this computer** and tap **Allow**.
3. In Android Studio, observe the device dropdown list in the top toolbar: your Redmi model (e.g. `Xiaomi 2201117TI` or `Redmi Note ...`) will appear with a green dot.

---

👉 **Next Step:** Proceed to [`12_ANDROID_INSTALLATION.md`](12_ANDROID_INSTALLATION.md) to build and run the application.
