# Android Application Architecture & Guide

The native **ProjectFlow Android Application** provides project tracking and risk monitoring on modern Android devices (Android 8.0 Oreo through Android 15, API level 26 to 35).

---

## Technical Stack
- **Language**: Java 17/21
- **Target SDK**: Android 15 (API 35)
- **Local Database**: AndroidX Room 2.6.1 with SQLite
- **Networking**: Retrofit 2.11.0 + OkHttp 4.12.0
- **Background Jobs**: AndroidX WorkManager 2.9.1 (`SyncWorker`)
- **UI Architecture**: ViewBinding, MaterialComponents, LiveData

---

## Application Modules & Screens
1. **SplashActivity**: Fast startup branding with session verification.
2. **LoginActivity**: Quick-switch presets for Administrator, Manager, and Member testing, with instant fallback if disconnected.
3. **DashboardFragment**: Real-time KPI summary (Workspaces, Projects, Tasks, Active Risks).
4. **ProjectsFragment**: Project listings, health badges (`ON TRACK`, `AT RISK`, `OFF TRACK`), and floating action button to create new initiatives.
5. **KanbanFragment**: Horizontal board with `TODO`, `IN PROGRESS`, and `DONE` task card streams.
6. **RiskRadarFragment**: Deterministic findings list with severity indicators and manual "Run Radar" trigger.
7. **SyncFragment**: Offline queue status, configurable server endpoint URL, and manual trigger for WorkManager sync.

---

## Deployment to Physical Device
1. Connect device via USB with Developer Mode and USB Debugging enabled.
2. Execute `INSTALL_ANDROID.bat` or run:
   ```bat
   & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8080 tcp:8080
   & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r P:\android-app\build\outputs\apk\debug\android-app-debug.apk
   ```
3. The APK will install and launch immediately on the attached device.
