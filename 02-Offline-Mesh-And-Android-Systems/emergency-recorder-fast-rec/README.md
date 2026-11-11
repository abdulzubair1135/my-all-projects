# Emergency Recorder (Fast Rec) 🎙️🚨

A native, high-performance Android emergency audio recording application built in **Kotlin** and **Jetpack Compose (Material 3)**.

Designed for rapid personal safety audio capture with minimal friction and zero UI interaction required during emergencies.

---

## ✨ Features

- **Hardware Double-Press Trigger**:
  - Double-press the physical **Volume Down** button at any time to instantly start or stop recording.
  - Distinct haptic vibration feedback for start, stop, and error states so you know recording is active without looking at the screen.
- **Background Foreground Service**:
  - Compliant with Android 14/15 (`foregroundServiceType="microphone"`).
  - Maintains a persistent, low-priority notification with a live duration timer and instant stop action.
  - Partial WakeLock ensures uninterrupted recording even if the phone screen turns off during capture.
- **Automatic Call Recording**:
  - Detects incoming and outgoing phone calls.
  - Automatically captures audio using speech-optimized streams (`VOICE_RECOGNITION`).
  - Automatically resolves and tags recordings with the caller's Contact Name and Phone Number (`Call_Name_Number_DateTime.m4a`).
  - Optional auto-speakerphone toggle for clear 2-way conversation recording.
- **Recording History & Interactive Player**:
  - Browse, share, and manage all recordings.
  - Built-in scrub slider with seek bar.
  - Fast-forward (+5s) and rewind (-5s) quick skip controls.
  - Real-time timestamp display (`MM:SS / MM:SS`).
- **Quick Settings Tile**:
  - Emergency Record tile in the Android notification shade for 1-tap capture.
- **Scoped Storage**:
  - Saved directly into standard Android Scoped MediaStore (`Recordings/EmergencyRecorder`) in voice-optimized AAC/M4A format.

---

## 🛠️ Tech Stack

- **Language**: Kotlin 2.0+
- **UI Framework**: Jetpack Compose with Material 3
- **Architecture**: MVVM / Service-Driven Architecture
- **Target SDK**: Android 14 / 15 (API 34 / 35), Min SDK: 26 (Android 8.0 Oreo)
- **Build System**: Gradle Version Catalog (`libs.versions.toml`)

---

## 🚀 Building & Installing

### Prerequisites
- Android Studio Ladybug / Koala or later
- JDK 17 or JDK 21
- Android SDK Platform 34 / 35

### Build via Gradle
```bash
./gradlew assembleDebug
```

### Install to Device via ADB
```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## 🔒 Privacy & Permissions

This application only accesses permissions explicitly enabled by the user for emergency recording:
- `RECORD_AUDIO`: Voice capture.
- `POST_NOTIFICATIONS`: Foreground service status indicator.
- `READ_PHONE_STATE`, `READ_CALL_LOG`, `READ_CONTACTS`: Automatic caller identification during call recording.
- `AccessibilityService`: Hardware Volume Down key event filtering (strictly zero window content inspection).
