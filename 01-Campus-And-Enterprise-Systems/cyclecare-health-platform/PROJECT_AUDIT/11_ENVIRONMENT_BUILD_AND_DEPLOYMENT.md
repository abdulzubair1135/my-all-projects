# 11_ENVIRONMENT_BUILD_AND_DEPLOYMENT.md — Environment, Build Pipeline, and Deployment

**Scope:** Step-by-step technical procedures for local workspace configuration, dependency resolution, Android APK compilation, backend execution, database migrations, and cloud continuous deployment.  
**Audit Date:** 2026-10-10  
**Evidence Standard:** Tested and validated on Windows 11 host, Android 15 physical device (`AI+ Nova 1 5G`), and Render Linux cloud container.

---

## 1. Prerequisites and Runtime Environment

| Prerequisite | Minimum Required | Verified Version | Purpose |
| :--- | :---: | :---: | :--- |
| **Operating System** | Windows 10/11 or Linux | Windows 11 / Linux (Render) | Host environment |
| **Node.js** | `>= 18.0.0` | `v20.x` | Backend runtime |
| **Java Development Kit** | JDK 17 | OpenJDK 17.0.10 | Android compilation & Gradle daemon |
| **Android SDK** | API 34 | Android SDK 34 / Build Tools 34.0.0 | Native mobile SDK |
| **Gradle** | 8.0+ | Gradle 8.9 (via Gradle Wrapper) | Android build automation |
| **ADB (Android Debug Bridge)**| Modern platform-tools | `platform-tools/adb.exe` | Device deployment & port forwarding |
| **PostgreSQL Pooler Access** | PostgreSQL 15 | Supabase Pooler Port 6543 | Relational database access |

---

## 2. Environment Variables & Secret Configuration

Configuration is loaded via `.env` in `backend/`:

| Environment Variable | Required / Optional | Default / Fallback in Code | Purpose |
| :--- | :---: | :--- | :--- |
| `PORT` | Optional | `5000` | HTTP port for REST server |
| `DATABASE_URL` | Essential | Supabase AWS pooler connection string | Direct PostgreSQL connection pool |
| `JWT_SECRET` | Essential | Configured SHA-256 secret in `authController.js` | HMAC signing key for JWT tokens |
| `ADMIN_SECRET_KEY` | Essential | `8c2e54885f922a59917e38d497e970aaa25287fe99a2e3fd` | Authorization secret for `x-admin-key` header |
| `RAZORPAY_KEY_ID` | Optional | Test key in `backend/src/config/razorpay.js` | Razorpay payment API identifier |
| `RAZORPAY_KEY_SECRET` | Optional | Test secret in `backend/src/config/razorpay.js`| Razorpay HMAC signature validation |
| `NODE_ENV` | Optional | `'development'` | Environment profile |

---

## 3. Local Backend Startup Procedures

### 3.1 One-Click Launcher (`start_control_panel.bat`)
Run the batch file located in the project root:
```cmd
start_control_panel.bat
```
**Internal Actions:**
1. Verifies Node.js installation.
2. Checks if the backend server is already running on port 5000.
3. If not running, launches `node src/server.js` in a minimized background console.
4. Waits for the port to bind and automatically opens `http://localhost:5000/admin-panel/admin.html` in the default web browser.

### 3.2 Manual Terminal Commands
```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Start development server
npm start
# OR with auto-reload:
npm run dev
```

---

## 4. Android Build & Deployment Procedures

### 4.1 Short Path Convention on Windows
> [!IMPORTANT]
> Because the local workspace path contains Unicode characters (`OneDrive\ドキュメント\arti astha`), Gradle commands should use the Windows 8.3 short directory format (`C:\Users\abdul\OneDrive\9831~1\ARTIAS~1\android`) to avoid file system encoding errors.

### 4.2 Compile Debug APK
```cmd
cmd /c "cd /d C:\Users\abdul\OneDrive\9831~1\ARTIAS~1\android && gradlew.bat assembleDebug"
```
- **Output Artifact:** `android/app/build/outputs/apk/debug/app-debug.apk`
- **Typical Build Time:** 19–23 seconds.

### 4.3 Install Directly onto Connected Device
```cmd
cmd /c "cd /d C:\Users\abdul\OneDrive\9831~1\ARTIAS~1\android && gradlew.bat installDebug"
```

### 4.4 Port Forwarding for Physical Device Testing
When testing the Android app against a local backend server (`http://localhost:5000`), establish reverse port forwarding over USB ADB:
```cmd
& "C:\Users\abdul\AppData\Local\Android\Sdk\platform-tools\adb.exe" reverse tcp:5000 tcp:5000
```
This enables the Android device to route `http://localhost:5000/` requests directly to the host machine's backend server.

---

## 5. Cloud Deployment Pipeline (Render & Cloudflare)

1. **Host:** Render Web Service (`https://cyclecare-57my.onrender.com`).
2. **Git Repository:** `https://github.com/cyclecarehelpcenter-sudo/CycleCare.git` (Branch: `main`).
3. **Continuous Deployment Trigger:** Any commit pushed to `origin/main` automatically triggers a Render cloud build:
   - Command: `npm install`
   - Start Command: `npm start`
4. **Health Verification Endpoint:**
   ```bash
   curl -i https://cyclecare-57my.onrender.com/api/v1/health
   ```
   Returns `HTTP 200 OK {"status":"ok","service":"CycleCare API","version":"1.0.0"}`.
