# RecoverX — Android Version Compatibility

## Compatibility Matrix

| Android Version | API Level | Storage Model | Permission Requirements | RecoverX Strategy |
| :--- | :--- | :--- | :--- | :--- |
| Android 7.0 - 8.1 | API 24 - 27 | Legacy Storage | `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE` | Direct File and MediaStore access |
| Android 9.0 | API 28 | Legacy Storage | `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE` | Direct File and MediaStore access |
| Android 10 | API 29 | Scoped Storage Intro | `requestLegacyExternalStorage=true` + MediaStore | MediaStore preferred, SAF fallback |
| Android 11 - 12L | API 30 - 32 | Scoped Storage Enforcement | `READ_EXTERNAL_STORAGE`, SAF for directories | MediaStore queries, SAF tree permissions |
| Android 13 | API 33 | Granular Media Permissions | `READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`, `READ_MEDIA_AUDIO` | Dynamic granular requests |
| Android 14 | API 34 | Partial Photo/Video Access | `READ_MEDIA_VISUAL_USER_SELECTED` | Handles selected vs full media permission |
| Android 15 | API 35 | Strict Scoped Storage & 16KB Pages | Granular media + SAF | Fully tested on physical Android 15 test device |
| Android 16 | API 36 | Privacy Sandbox & Storage Isolation | Granular media + Photo Picker + SAF | Adaptive runtime permission queries |

## Runtime Permission Handling
- RecoverX checks `Build.VERSION.SDK_INT` dynamically.
- When requesting media access on API 33+, it requests granular permissions (`READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`, `READ_MEDIA_AUDIO`).
- On API 34+, it gracefully handles `READ_MEDIA_VISUAL_USER_SELECTED` partial authorization without crashing.
- On API 24-32, it falls back to `READ_EXTERNAL_STORAGE`.
- When accessing arbitrary directories or SD card folders, RecoverX guides the user through the Storage Access Framework (SAF) `ACTION_OPEN_DOCUMENT_TREE` picker.
