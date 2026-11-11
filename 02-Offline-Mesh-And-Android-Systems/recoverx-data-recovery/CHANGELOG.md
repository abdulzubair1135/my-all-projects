# Changelog

All notable changes to the RecoverX project are documented in this file.

## [1.0.1] - 2026-10-17
### Added & Enhanced
- **Strict Deleted-Only Recovery Filter:** Scan results (`ScanResultsScreen`) and Recovery Center (`RecoveryCenterScreen`) now strictly filter out ordinary storage files (`EXISTING_FILE`), showing **ONLY** recoverable deleted media, system trash items, and cached thumbnails.
- **Deep Thumbnail Cache & Trash Scanner:** Enhanced `ThumbnailSource` with deep filesystem traversal across internal and removable storage, scanning `.thumbnails`, `.trash`, `.trashed-*`, and `LOST.DIR` with magic byte validation (JPEG, PNG, GIF, MP4). Discovered 5,500+ cached photo thumbnails on physical test device.
- **MediaStore Trash Query:** Enabled explicit querying of `MediaStore.QUERY_ARG_MATCH_TRASHED = MATCH_ONLY` on Android 11+ (API 30+) to recover files in Android's Gallery Trash bin.
- **Instant Photo/Video Preview Navigation:** Tapping any image candidate in scan results immediately opens the high-resolution pinch-to-zoom `ImagePreviewScreen`, while video candidates launch AndroidX Media3 `VideoPreviewScreen`.
- **List-Row Image Previews:** Integrated Coil `SubcomposeAsyncImage` directly into `DiscoveredItemRow`, displaying actual photo thumbnails in each row instead of static generic vector icons.
- **Crash & Reparse Mitigation:** Resolved OneDrive cloud placeholder reparse points and missing imports. Verified 11/11 unit tests passing and deployed updated APK to physical device.

## [1.0.0] - 2026-10-17
### Added
- Complete Native Android Storage Explorer & Data Recovery Application.
- Jetpack Compose + Material 3 UI with full dark/light/system theming and high-contrast styling.
- 27 fully functional navigation destinations covering Onboarding, Dashboard, Explorer, Scanner, Preview, Recovery, Diagnostics, and Settings.
- `PermissionCoordinator` providing adaptive permission handling across Android 7 (API 24) through Android 16 (API 36).
- `MediaStoreDiscoverySource` and `FolderDiscoverySource` for ContentResolver and Storage Access Framework (SAF) discovery.
- `SignatureRegistry` inspecting binary headers for JPEG, PNG, GIF, MP4, PDF, and ZIP magic bytes.
- `ThumbnailSource` discovering cached thumbnails, explicitly classified as `THUMBNAIL_ONLY`.
- Safe `StreamingRestorer` with 64KB bounded I/O, `CollisionResolver`, and `IntegrityValidator`.
- Image preview with multi-touch pinch-to-zoom (up to 5x) and pan via Coil.
- Video preview with AndroidX Media3 ExoPlayer and hardware-accelerated playback.
- File forensics panel computing real-time streaming SHA-256 hashes.
- Native SQLite database (`RecoverXDatabaseHelper`) managing scan sessions, discovered items, and recovery records.
- Standalone unit test suite (`scripts/run_unit_tests.ps1`) executing 11 tests with 100% pass rate.
- Verified on physical Android 15 (API 35) device (`Nova_1_5G`) via ADB.
- Release artifacts: `release/RecoverX-v1.0.0-debug.apk` and `release/RecoverX-v1.0.0-release-unsigned.apk`.
