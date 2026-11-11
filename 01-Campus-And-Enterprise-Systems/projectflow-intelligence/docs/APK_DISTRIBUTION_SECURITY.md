# ProjectFlow Intelligence — APK Distribution Security & Integrity Standard

## 1. Security Architecture & Threat Model

Distributing Android applications directly between devices and via out-of-band channels presents distinct security challenges. ProjectFlow Intelligence enforces enterprise-grade mitigations against each threat vector:

| Threat Vector | Mitigation Strategy | Implementation |
|---|---|---|
| **Man-in-the-Middle (MitM) Tampering** | Streaming cryptographic SHA-256 verification | `ApkDistributionManager.computeSha256(File)` |
| **Directory Traversal & Path Injection** | Sandboxed `FileProvider` with non-exported configuration | `android:exported="false"`, `grantUriPermissions="true"` |
| **Split-APK Incompatible Distribution** | Standalone APK verification via `PackageParser` | `PackageManager.getPackageArchiveInfo()` check |
| **Unauthorized File Access** | Scoped temporary read grants | `Intent.FLAG_GRANT_READ_URI_PERMISSION` only |
| **Corrupted Download Execution** | Atomic temporary write & verification prior to promotion | Writes to `.tmp` file; validates hash before renaming |
| **Impersonation / Malicious APK** | Strict MIME enforcement & canonical naming | `application/vnd.android.package-archive` |

---

## 2. Cryptographic Checksum Validation

When downloading an official release from the backend:
1. The remote release metadata provides an authoritative `sha256Checksum` generated during release build signing.
2. The download streams chunk-by-chunk through `MessageDigest.getInstance("SHA-256")`.
3. If the calculated digest differs from the expected checksum:
   - The corrupted artifact is immediately deleted from disk.
   - An `IntegrityException` is thrown.
   - Sharing is halted, preventing compromised packages from propagating.

```java
// Streaming SHA-256 calculation excerpt from ApkDistributionManager
MessageDigest digest = MessageDigest.getInstance("SHA-256");
byte[] buffer = new byte[8192];
int read;
while ((read = is.read(buffer)) != -1) {
    digest.update(buffer, 0, read);
}
String computedHash = bytesToHex(digest.digest());
if (!computedHash.equalsIgnoreCase(expectedHash)) {
    throw new SecurityException("Hash mismatch: APK may be corrupted or tampered.");
}
```

---

## 3. Secure FileProvider Configuration

Modern Android enforces strict file isolation. Directly sharing a `file:///` URI causes a security exception on Android 7.0+ (`FileUriExposedException`).

### Rules Enforced:
1. **Never export the FileProvider:**
   ```xml
   <provider
       android:name="androidx.core.content.FileProvider"
       android:authorities="${applicationId}.fileprovider"
       android:exported="false"
       android:grantUriPermissions="true">
       <meta-data
           android:name="android.support.FILE_PROVIDER_PATHS"
           android:resource="@xml/file_paths" />
   </provider>
   ```
2. **Strictly bounded path mappings:**
   Only internal `cache/releases/` and `files/releases/` subpaths are exposed to the FileProvider. Root device storage, external storage, and database directories remain inaccessible.
3. **Transient Access Control:**
   Receiving applications (e.g. WhatsApp, Bluetooth, Nearby Share) are granted temporary, ephemeral read rights that terminate as soon as the receiving application finishes processing the intent.

---

## 4. Protection Against Split-APK Distribution Failures

When using Android's app bundles (AAB), the operating system installs split APKs (e.g., `base.apk`, `split_config.arm64_v8a.apk`, `split_config.xxhdpi.apk`).
Attempting to share only `sourceDir` when installed via split APKs results in `INSTALL_FAILED_INVALID_APK` on the recipient's phone.

`ApkDistributionManager` validates this condition:
```java
PackageInfo info = context.getPackageManager().getPackageArchiveInfo(apkFile.getAbsolutePath(), 0);
if (info == null || info.packageName == null) {
    throw new IllegalStateException("Installed APK is not a valid standalone package.");
}
```
If split installations are detected, the app prioritizes fetching the universal, standalone signed APK from the ProjectFlow distribution backend instead of sharing an unviable local split.

---

## 5. Security Checklist for Production Release
- [x] APK signed with production release keystore (v1 + v2 + v3 signing schemes).
- [x] FileProvider declared with `android:exported="false"`.
- [x] Checksum validation running on client before sharing.
- [x] Backend download endpoint protected with rate limiting & ETag caching.
- [x] MIME type strictly locked to `application/vnd.android.package-archive`.
- [x] No persistent write permissions granted to external recipients.
