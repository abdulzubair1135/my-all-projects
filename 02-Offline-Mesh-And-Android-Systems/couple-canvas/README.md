# 💕 Couple Canvas

> **"Two people. One canvas. Draw together."**

Couple Canvas is a production-quality, local-first, P2P-first collaborative drawing Android application built with **Kotlin**, **Jetpack Compose**, **Material 3**, **Room Database**, **WebRTC DataChannel**, and a lightweight **Node.js WebSocket signaling server**.

---

## 🌟 Core Architecture & Privacy Principles

- **Local-First Artwork**: All drawings, canvas vector strokes, exported PNG/JPG images, and galleries are saved **exclusively on users' local devices** using Room Database.
- **Direct P2P Sync**: Live stroke points, sticker movements, text, shapes, cursor tracking, emoji particles, and mini-chat messages stream directly between devices via **WebRTC DataChannel**.
- **Minimal Central Server**: The central server does NOT store artwork, drawings, or messages. It is used strictly for short-lived session coordination (room creation, room joining, WebRTC offer/answer handshakes).
- **Offline-First Resilience**: Users can continue drawing locally even if internet connectivity drops. Local vector operations persist deterministically.

---

## 📁 Repository Structure

```
couple draw/
├── CoupleCanvas/                  # Android Application Root
│   ├── app/
│   │   ├── build.gradle.kts       # Android App Gradle configuration
│   │   ├── src/main/
│   │   │   ├── AndroidManifest.xml # Permissions & App Config
│   │   │   └── java/com/couplecanvas/app/
│   │   │       ├── data/          # Room DB, DAOs, Entities, DataStore
│   │   │       ├── domain/        # Vector models, operations, protocols
│   │   │       ├── drawing/       # Vector engine, Bézier smoothing, renderer
│   │   │       ├── realtime/      # WebRTC PeerConnection & WebSocket client
│   │   │       └── ui/            # Jetpack Compose screens & theme
│   ├── build.gradle.kts           # Root Gradle build script
│   └── gradle/libs.versions.toml  # Gradle Version Catalog
│
├── signaling-server/              # Node.js WebRTC Signaling Server
│   ├── package.json               # Express, ws, helmet dependencies
│   └── server.js                  # WebSocket room coordination & relay
└── README.md                      # Complete setup & deployment guide
```

---

## ⚙️ Prerequisites

- **JDK**: Java 17 or Java 21 (Verified working with Java 25)
- **Node.js**: Node.js v18+ (Verified working with Node.js v25.1.0)
- **Android Studio**: Android Studio Jellyfish / Koala / Ladybug or newer
- **Android SDK**: Compile SDK 35, Min SDK 26 (Android 8.0+)

---

## 🚀 Step 1: Run the Node.js Signaling Server

1. Open terminal in the `signaling-server` directory:
   ```bash
   cd signaling-server
   ```
2. Install server dependencies:
   ```bash
   npm install
   ```
3. Start the server:
   ```bash
   npm start
   ```
   *The server will start on port `8080` (e.g., `ws://localhost:8080` or `ws://10.0.2.2:8080` for Android Emulator).*

---

## 📱 Step 2: Configure & Build the Android App

1. Open **Android Studio** and choose **Open Folder** -> Select `couple draw/CoupleCanvas`.
2. Sync Gradle files (`Gradle Sync`).
3. To test on Android Emulator:
   - Default signaling URL is pre-configured to `ws://10.0.2.2:8080`.
4. To test on Physical Devices (Same Wi-Fi network):
   - Find your computer's local IP address (e.g. `192.168.1.50`).
   - Open **Settings** inside the app and set the Signaling Server URL to `ws://192.168.1.50:8080`.

---

## 📦 Step 3: Build Debug APK & Release AAB

### Build Debug APK
Run in terminal inside `CoupleCanvas`:
```bash
./gradlew assembleDebug
```
Output APK location:
`CoupleCanvas/app/build/outputs/apk/debug/app-debug.apk`

### Build Signed Release App Bundle (AAB) for Google Play
1. Create a production release keystore:
   ```bash
   keytool -genkey -v -keystore couple-canvas-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias couplecanvas
   ```
2. Configure signing in `CoupleCanvas/app/build.gradle.kts`:
   ```kotlin
   signingConfigs {
       create("release") {
           storeFile = file("couple-canvas-key.jks")
           storePassword = "YOUR_STORE_PASSWORD"
           keyAlias = "couplecanvas"
           keyPassword = "YOUR_KEY_PASSWORD"
       }
   }
   ```
3. Run the bundle task:
   ```bash
   ./gradlew bundleRelease
   ```
Output AAB location:
`CoupleCanvas/app/build/outputs/bundle/release/app-release.aab`

---

## 💰 Step 4: AdMob Integration Guide

- **Test Application ID**: `ca-app-pub-3940256099942544~3347511713` (Pre-configured in `AndroidManifest.xml`).
- **Test Banner Ad Unit ID**: `ca-app-pub-3940256099942544/6300978111` (Pre-configured in `strings.xml`).

When deploying to production:
1. Register your app in the [Google AdMob Console](https://admob.google.com).
2. Replace the test App ID in `AndroidManifest.xml` with your production AdMob App ID.
3. Replace the test Banner Unit ID in `strings.xml` with your production Banner Unit ID.

---

## 🛡️ Play Store Release & Privacy Policy Checklist

- [x] **Data Safety Declaration**: Select **No data shared with third parties** for drawing binaries; all drawings remain 100% on device.
- [x] **Privacy Policy URL**: Host the privacy terms outlined in the app's `PrivacyPolicyScreen.kt`.
- [x] **Camera & Network Permissions**: Declare `CAMERA` (optional for QR scanner) and `INTERNET`.
- [x] **Abuse Protection**: Report & Block functionality implemented to satisfy Google Play User Generated Content policies.

---

## 📄 License

Distributed under the MIT License.
