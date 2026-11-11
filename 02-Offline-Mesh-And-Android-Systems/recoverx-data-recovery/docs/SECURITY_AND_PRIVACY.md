# RecoverX — Security & Privacy Architecture

## Strict Privacy Principles
- **100% Offline-First**: No network permissions are required or requested for scanning, file inspection, or file restoration. All file operations occur strictly locally on the user's device.
- **Zero Cloud Exfiltration**: No user files, thumbnails, names, or metadata are ever transmitted off the device.
- **No Unnecessary Permissions**: Only storage and media permissions required for file discovery are requested. No contacts, SMS, microphone, camera, or location access.
- **Path Traversal Protection**: All user-chosen filenames and paths are sanitized against relative path traversal attacks (e.g., `../`).
- **Destructive Operation Safety**: RecoverX NEVER overwrites or deletes existing source files during scan or recovery operations.
