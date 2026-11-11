# CYCLECARE — DEPLOYMENT & CONFIGURATION GUIDE
## Environment Variables, Render Cloud Setup, Supabase Migrations & Android Release Builds

---

## 1. PREREQUISITES & SYSTEM REQUIREMENTS (आवश्यक सॉफ्टवेयर और टूल्स)

CycleCare full-stack system deploy karne ke liye niche diye gaye tools pre-installed hone chahiye:

| Component | Minimum Version | Recommended Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Node.js** | v18.16.0 LTS | v20.11.0 LTS | Backend server runtime |
| **npm** | v9.0.0 | v10.2.0 | Package dependency manager |
| **Java Development Kit (JDK)**| JDK 17 | JDK 17.0.9 (Temurin / Oracle)| Android Gradle build compilation |
| **Android SDK / Studio** | API Level 26 (Android 8.0) | API Level 34 (Android 14) | Mobile app packaging |
| **PostgreSQL Database** | PostgreSQL 14+ | Supabase Cloud PostgreSQL 15 | Relational cloud storage |
| **Git** | v2.30.0 | v2.40+ | Version control & Render auto-deploy |

---

## 2. ENVIRONMENT VARIABLES CONFIGURATION (`.env`)

Backend root directory (`backend/.env`) mein niche diye gaye environment parameters configure hone chahiye:

```ini
# ========================================================
# CYCLECARE BACKEND PRODUCTION CONFIGURATION
# ========================================================

# Server Port & Mode
PORT=5000
NODE_ENV=production

# Supabase PostgreSQL Connection Pooler (Port 6543)
DATABASE_URL=postgres://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u#@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres

# Supabase API Credentials
SUPABASE_URL=https://zbgzrkdmvtofyikksptq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpiZ3pya2RtdnRvZnlpa2tzcHRxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjc2OTcxNzEsImV4cCI6MjA0MzI3MzE3MX0.sS_fFk4N2_8zO45W7eH8vI73...

# Cryptographic Token Signing Secrets
JWT_SECRET=CycleCareSuperSecureProductionJwtSecretKey_2026!
JWT_EXPIRES_IN=7d

# Admin Access Passphrase
ADMIN_API_KEY=CycleCareAdminMasterSecretKey2026#

# Delivery Demo Overrides
DEMO_DELIVERY_OTP=4821
```

---

## 3. DATABASE MIGRATIONS EXECUTION (डेटाबेस सेटअप)

Supabase PostgreSQL database par tables create ya update karne ke liye sequential migrations run karein:

```bash
# PostgreSQL CLI (psql) se direct run karein:
psql "postgres://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u#@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres" -f database/migrations/001_initial_schema.sql
psql "postgres://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u#@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres" -f database/migrations/002_partner_and_circle.sql
psql "postgres://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u#@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres" -f database/migrations/003_store_and_orders.sql
psql "postgres://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u#@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres" -f database/migrations/004_telemetry_and_errors.sql
psql "postgres://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u#@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres" -f database/migrations/005_trusted_circle_and_delivery.sql
psql "postgres://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u#@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres" -f database/migrations/006_reciprocal_relationships.sql
```

---

## 4. BACKEND DEPLOYMENT ON RENDER CLOUD (क्लाउड होस्टिंग)

Render Web Service par backend host karne ke steps:

1. **New Web Service:** Render dashboard par jakar *"New Web Service"* select karein aur GitHub repo connect karein.
2. **Root Directory:** Set root directory to `backend`.
3. **Environment:** `Node`.
4. **Build Command:**
   ```bash
   npm install
   ```
5. **Start Command:**
   ```bash
   npm start
   ```
6. **Environment Variables:** Render dashboard ke "Environment" tab mein upar diye gaye `.env` values add karein.
7. **Health Check Path:** `/api/v1/health` configure karein. Render auto-deploy hone par status "Live" dikhayega.

---

## 5. ANDROID APP COMPILATION & RELEASE SIGNING (एंड्रॉयड बिल्ड)

### 5.1 Debug APK Compilation
Local testing aur emulator evaluation ke liye debug APK build karein:
```bash
cd android
./gradlew clean assembleDebug
```
Output File: `android/app/build/outputs/apk/debug/app-debug.apk`

### 5.2 Production Release Keystore Generation
Google Play Store publication ke liye cryptographic signing keystore generate karein:
```bash
keytool -genkey -v -keystore cyclecare-release.jks -alias cyclecare-key -keyalg RSA -keysize 2048 -validity 10000
```

### 5.3 Release APK Compilation
`android/app/build.gradle` mein `signingConfigs` define karke release build generate karein:
```bash
./gradlew assembleRelease
```
Output File: `android/app/build/outputs/apk/release/app-release.apk`

---

## 6. ONE-CLICK LOCAL EVALUATION (लोकल रन कमांड्स)

Evaluator ya examiner ke laptop par bina kisi hassle ke complete project run karne ke liye:

1. **Step 1:** Double-click `start_control_panel.bat` (Starts backend on port 5000 and opens Admin Panel).
2. **Step 2:** Open Android Studio -> Select `android/` -> Click **Run 'app'** (Green play button) on connected emulator or physical device.
3. **Step 3:** Login as delivery demo agent:
   - Email: `delivery.demo@cyclecare.app`
   - Password: `CycleCareDemo123!`
