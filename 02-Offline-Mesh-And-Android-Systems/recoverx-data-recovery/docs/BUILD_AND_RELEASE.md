# RecoverX — Build and Release Guide

## Prerequisites
- JDK 21 (Android Studio JBR recommended)
- Android SDK Platforms: android-34, android-35, android-36
- Android Build-Tools: 35.0.0 or 36.0.0

## Build Commands (PowerShell)
```powershell
# Assemble Debug APK
.\gw.ps1 assembleDebug

# Install on connected device/emulator
.\gw.ps1 installDebug

# Run Unit Tests
.\gw.ps1 testDebugUnitTest
```

## Release Artifacts Location
- Debug APK: `app/build/outputs/apk/debug/app-debug.apk`
- Release APK: `app/build/outputs/apk/release/app-release-unsigned.apk` (or signed when key configured)
