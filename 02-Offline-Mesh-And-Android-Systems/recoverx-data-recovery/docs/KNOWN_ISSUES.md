# RecoverX — Known Issues and Mitigations

| Issue ID | Description | Impact | Mitigation / Status |
| :--- | :--- | :--- | :--- |
| ISS-01 | Android 11+ restricts access to `/Android/data` and `/Android/obb` even with SAF | Cannot list third-party private app storage without root | RecoverX clearly documents this limitation to the user and skips inaccessible paths gracefully |
| ISS-02 | File TRIM on modern flash renders deleted blocks zeroed | Deep raw sector carving on encrypted internal storage is physically impossible without low-level chip-off | RecoverX identifies salvageable trash, cache, thumbnails, and alternate copies rather than making impossible claims |
| ISS-03 | Windows Command Prompt (CMD) codepage issues with Japanese characters in directory paths | `gradlew.bat` might fail to resolve wrapper path | Provided `gw.ps1` PowerShell launcher invoking Gradle wrapper directly via Java |
