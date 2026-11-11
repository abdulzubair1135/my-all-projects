# RecoverX

**Native Android Storage Explorer & Forensics-Informed Data Recovery Application**

RecoverX is a native Android application engineered to discover accessible device storage, preview photos and videos, detect extension and MIME mismatches, search for cached thumbnails and alternate copies, and safely restore accessible files without ever fabricating scan results or making false promises.

---

## Key Capabilities

1. **Storage Explorer**:
   - Comprehensive categorizer for Photos, Videos, Audio, Documents, Archives, Downloads, and Other files.
   - Real-time search, multi-category filter chips, and timestamp sorting.
   - Storage Access Framework (SAF) folder picker for custom directory and SD card browsing.

2. **Honest Data Recovery Engine**:
   - MediaStore Trash inspection (`IS_TRASHED` flag where accessible on API 30+).
   - High-resolution cached thumbnail discovery, explicitly marked as `Thumbnail Only`.
   - Alternate backup copies detection across permitted directory trees.
   - Binary file signature (magic bytes) recognition for JPEG, PNG, GIF, MP4, PDF, and ZIP.
   - Clear candidate classifications: Existing File, Backup/Copy, Thumbnail Only, Trash Item, Carved Header, Corrupted File.

3. **Safe Streaming Restoration**:
   - Bounded 64KB streaming copy preventing Out-Of-Memory (OOM) errors on large files.
   - Conflict-free destination naming via `CollisionResolver` (`file (1).jpg`).
   - Post-restoration integrity validation (byte count check and magic bytes header verification).
   - Target picker: Standard app directory (`Downloads/RecoverX_Restored`) or custom SAF user-selected folder/SD card.

4. **Media Previews & Forensics**:
   - Multi-touch pinch-to-zoom (up to 5x) and pan image viewer via Coil.
   - AndroidX Media3 ExoPlayer video preview with play, pause, seek, and lifecycle release.
   - Detailed forensics panel with real-time streaming SHA-256 hash calculation.

5. **Privacy & Security**:
   - 100% Offline: Zero network permissions, zero cloud exfiltration.
   - Read-only source operations: RecoverX never alters or deletes original source files.

---

## Project Structure
```
RecoverX/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── AndroidManifest.xml
│   │   │   ├── java/com/recoverx/
│   │   │   │   ├── app/           # RecoverXApplication, AppContainer
│   │   │   │   ├── core/          # PermissionCoordinator, StorageInspector, AppError
│   │   │   │   ├── data/          # SQLite Database, DAOs, Entities
│   │   │   │   ├── discovery/     # MediaStore, Folder, Trash, Thumbnail, Signature Sources
│   │   │   │   ├── recovery/      # RecoveryManager, StreamingRestorer, CollisionResolver
│   │   │   │   ├── scanner/       # ScanCoordinator, DuplicateDetector
│   │   │   │   ├── navigation/    # Screen routes, RecoverXNavGraph (all 27 destinations)
│   │   │   │   └── ui/            # Compose screens, components, theme
│   │   │   └── res/
│   │   └── test/                  # Unit tests (JUnit 4)
├── docs/                          # Comprehensive architecture and limitations documentation
├── release/                       # Built APK artifacts
├── scripts/                       # Helper scripts (run_unit_tests.ps1)
├── gw.ps1                         # PowerShell Gradle runner
├── build.gradle.kts
└── settings.gradle.kts
```

---

## Build & Test Instructions

### Prerequisites
- JDK 21 (Android Studio JBR recommended)
- Android SDK (API 34, 35, or 36)

### Build APKs
```powershell
# Assemble Debug APK
.\gw.ps1 assembleDebug

# Assemble Release APK
.\gw.ps1 assembleRelease
```

### Run Unit Tests
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_unit_tests.ps1
```

### Install on Device via ADB
```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r release\RecoverX-v1.0.0-debug.apk
```

---

## Distribution Artifacts
- **Debug APK**: `release/RecoverX-v1.0.0-debug.apk` (21.3 MB)
- **Release APK**: `release/RecoverX-v1.0.0-release-unsigned.apk` (14.4 MB)
