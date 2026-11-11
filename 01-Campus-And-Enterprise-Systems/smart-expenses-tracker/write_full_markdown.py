# -*- coding: utf-8 -*-
"""
Generates the comprehensive 30-Chapter Markdown Handbook: SMART_EXPENSES_HINGLISH_MASTER_GUIDE.md
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

md_content = """# 📱 SMART EXPENSES TRACKER - 30-PAGE COMPLETE HINGLISH MASTER HANDBOOK

> **Project Name:** Smart Expenses Tracker  
> **Mobile App Architecture:** Pure Java 17 + XML Layouts (Zero Kotlin)  
> **Backend Relay Server:** Node.js (v18+) + Express + TypeScript (Port 4000)  
> **Admin Control Panel:** React 18 + Vite + Tailwind CSS (Port 5173)  
> **Cloud Database:** Supabase Managed PostgreSQL 15 + Row Level Security (RLS)  
> **Academic Institution:** SRK Institute of Management and Computer Application, Sapeda  
> **Affiliated University:** K.S.K.V. Kachchh University, Bhuj – Kachchh, Gujarat  
> **Program & Semester:** Bachelor of Computer Applications (BCA) – Semester V  
> **Subject:** Mobile Application Development (Academic Year 2026–2027)  
> **Project Guide:** Mr. Prakash Lambha (Assistant Professor)  
> **Submitted By:** Asther & Divya  
> **Official GitHub Repository:** [https://github.com/smartexpensehelp-sketch](https://github.com/smartexpensehelp-sketch)  

---

## 📑 Quick Navigation (All 30 Chapters)

- [Page 1: Cover Page & Credentials](#page-1-cover-page--credentials)
- [Page 2: Master Index & Padhne Ka Tarika](#page-2-master-index--padhne-ka-tarika)
- [Page 3: Smart Expenses Tracker Kya Hai?](#page-3-smart-expenses-tracker-kya-hai)
- [Page 4: Core System Architecture & 3-Tier Data Flow](#page-4-core-system-architecture--3-tier-data-flow)
- [Page 5: Strict Financial Rules & Minor Units (Paise System)](#page-5-strict-financial-rules--minor-units-paise-system)
- [Page 6: Tech Stack Overview (Kya-Kya Use Hua Hai)](#page-6-tech-stack-overview-kya-kya-use-hua-hai)
- [Page 7: Android Native Stack Deep Dive](#page-7-android-native-stack-deep-dive)
- [Page 8: Backend Server & Admin Web Stack](#page-8-backend-server--admin-web-stack)
- [Page 9: Cloud Database & Security Stack](#page-9-cloud-database--security-stack)
- [Page 10: Android App Structure & MVVM Architecture](#page-10-android-app-structure--mvvm-architecture)
- [Page 11: Room Database Entities & DAO Implementation](#page-11-room-database-entities--dao-implementation)
- [Page 12: Voice Assistant Engine (Bilingual AI)](#page-12-voice-assistant-engine-bilingual-ai)
- [Page 13: Push Notifications & Smart Back Navigation](#page-13-push-notifications--smart-back-navigation)
- [Page 14: Backend Server Architecture (server.ts)](#page-14-backend-server-architecture-serverts)
- [Page 15: REST API Endpoints Reference](#page-15-rest-api-endpoints-reference)
- [Page 16: Idempotency & Sync Engine Algorithms](#page-16-idempotency--sync-engine-algorithms)
- [Page 17: Supabase PostgreSQL Database Schema](#page-17-supabase-postgresql-database-schema)
- [Page 18: Row Level Security (RLS) & Multi-Tenancy](#page-18-row-level-security-rls--multi-tenancy)
- [Page 19: React Web Admin Control Panel](#page-19-react-web-admin-control-panel)
- [Page 20: Prerequisites & Environment Setup](#page-20-prerequisites--environment-setup)
- [Page 21: Step-by-Step Running Guide: Automated (.bat Files)](#page-21-step-by-step-running-guide-automated-bat-files)
- [Page 22: Step-by-Step Running Guide: Manual Terminal Commands](#page-22-step-by-step-running-guide-manual-terminal-commands)
- [Page 23: Real Android Phone USB Installation (Nova 1 5G)](#page-23-real-android-phone-usb-installation-nova-1-5g)
- [Page 24: Batch Scripts Deep Breakdown (Part 1: START & STOP)](#page-24-batch-scripts-deep-breakdown-part-1-start--stop)
- [Page 25: Batch Scripts Deep Breakdown (Part 2: INSTALL & RUN)](#page-25-batch-scripts-deep-breakdown-part-2-install--run)
- [Page 26: Offline-First Synchronization Lifecycle](#page-26-offline-first-synchronization-lifecycle)
- [Page 27: Troubleshooting: Top Common Errors & Exact Fixes](#page-27-troubleshooting-top-common-errors--exact-fixes)
- [Page 28: Advanced Debugging & Log Monitoring](#page-28-advanced-debugging--log-monitoring)
- [Page 29: Project File Structure Directory Map](#page-29-project-file-structure-directory-map)
- [Page 30: University Viva & Practical Q&A](#page-30-university-viva--practical-qa)

---

## Page 1: Cover Page & Credentials

Smart Expenses Tracker ek modern, local-first personal financial ledger ecosystem hai jo students, daily wage earners aur working professionals ke liye banaya gaya hai.

### Key Highlights:
1. **Zero-Lag Offline Recording:** Phone chahe flight mode me ho ya bina internet ke, instant data entry hoti hai.
2. **Bank-Grade Calculation Precision:** Float ya double data type ko poori tarah ban karke integer minor units (`long` in Paise) use kiya gaya hai.
3. **Automated Cloud Backup:** Android Jetpack WorkManager background me bina battery drain kiye Supabase PostgreSQL cloud par data push karta hai.
4. **Bilingual Voice Engine:** Hindi aur English voice input ("500 mile save kardo", "spent 200 for lunch") se automatic transaction parse ho jata hai.
5. **Zero-Knowledge Privacy:** Web Admin Panel system diagnostics check kar sakta hai, lekin user ke private balances ko nahi dekh sakta.

---

## Page 2: Master Index & Padhne Ka Tarika

Is guide ko 30 main logical pages/sections me divide kiya gaya hai:
- **Part 1 (Pages 1–5):** System Overview, Core Need, Architecture aur Minor Units.
- **Part 2 (Pages 6–9):** Full Tech Stack (Android, Backend, Admin, Database).
- **Part 3 (Pages 10–13):** Android App Deep Dive (MVVM, Room, Voice AI, Smart Back).
- **Part 4 (Pages 14–19):** Backend Server, REST APIs, Supabase DB, RLS aur React Admin.
- **Part 5 (Pages 20–25):** Setup, Installation, .bat Scripts aur Real Phone USB Debugging.
- **Part 6 (Pages 26–30):** Sync Lifecycle, Error Troubleshooting, Directory Map aur Viva Q&A.

---

## Page 3: Smart Expenses Tracker Kya Hai?

### Asli Zindagi Ki Samasya (The Real-World Problem)
Aam financial apps (jaise Spendee, Money Manager wagera) me 3 major problems aati hain:
1. **Network Lock:** Weak internet ya basement me app khulte hi loading spinner ghoomne lagta hai.
2. **Floating Point Rounding Error:** 0.1 + 0.2 = 0.30000000000000004 ban jata hai, jisse accounts ka balance match nahi hota.
3. **Data Privacy:** Users ka financial ledger unencrypted form me admin dekh sakte hain.

### Humara Solution
Smart Expenses Tracker in teeno pareshaniyon ko khatam karta hai:
- Pehle phone ke Room SQLite me 0ms latency me save hota hai.
- Har amount ko integer Paise me store kiya jata hai.
- Supabase PostgreSQL me Row Level Security (RLS) se har user ka data isolated rehta hai.

---

## Page 4: Core System Architecture & 3-Tier Data Flow

System 3 independent tiers me divide hai:

```
[ Tier 1: Mobile Client ]   <--- Local SQLite Room DB (Offline First, 0ms latency)
           |
     Sync Push / Pull (JSON over HTTP/HTTPS)
           v
[ Tier 2: Backend Relay ]   <--- Node.js + Express + TypeScript (Port 4000)
           |                     (JWT Verification, Idempotency Deduplication)
     PostgreSQL Connection (SSL Encrypted)
           v
[ Tier 3: Cloud & Admin ]   <--- Supabase PostgreSQL 15 + React Vite Admin (Port 5173)
                                 (Row Level Security, Zero-Knowledge Privacy Wall)
```

---

## Page 5: Strict Financial Rules & Minor Units (Paise System)

### Floating Point Bug Ban Kyu Hai?
IEEE-754 standard ke mutabiq binary floats decimals ko exact represent nahi kar paate:
- ₹500.10 + ₹200.20 float me ban sakta hai ₹700.3000000000001!

### Minor Units Rule
Humne poore project me strict rule enforce kiya hai:
- **Display par:** ₹ 500.00
- **Database & Code me:** `50000` (Paise) as `long` in Java aur `BIGINT` in PostgreSQL.

```java
// Java Conversion Utility
public static long rupeesToPaise(String rupees) {
    return new BigDecimal(rupees.trim()).multiply(new BigDecimal("100")).longValue();
}

public static String formatPaiseToRupees(long paise) {
    long r = paise / 100;
    long p = Math.abs(paise % 100);
    return String.format(Locale.getDefault(), "₹ %,d.%02d", r, p);
}
```

---

## Page 6: Tech Stack Overview (Kya-Kya Use Hua Hai)

| Layer | Technologies Used | Key Responsibilities |
| :--- | :--- | :--- |
| **Android Client** | Pure Java 17, XML, Material Design 3 | UI rendering, Room SQLite local cache, SpeechRecognizer |
| **Background Sync** | Android Jetpack WorkManager | Network-constrained background cloud synchronization |
| **Relay Backend** | Node.js v18, Express 4.19, TypeScript | REST APIs, JWT authentication, Idempotency deduplication |
| **Admin Web UI** | React 18, Vite, Tailwind CSS, Lucide | Telemetry metrics, service health probes, audit logs |
| **Cloud Database** | Supabase Managed PostgreSQL 15 | Multi-tenant relational storage, Row Level Security |
| **Automation** | Windows Batch (.bat), Android ADB | 1-click startup, port release, USB installation |

---

## Page 7: Android Native Stack Deep Dive

1. **Pure Java 17:** University syllabus BCA Sem V ke pure Object-Oriented principles ko follow karta hai. No third-party Kotlin runtime overhead.
2. **Room SQLite ORM (v2.6.1):** Compile-time SQL verification, LiveData integration, single-thread executor background writes.
3. **Jetpack WorkManager:** Doze-mode friendly background scheduler jo phone reboot hone par bhi sync retain rakhta hai.
4. **XML Layouts:** Responsive ConstraintLayout, MaterialCardView, CoordinatorLayout with emerald green branding.

---

## Page 8: Backend Server & Admin Web Stack

1. **Express.js (TypeScript):** Static typing guarantees that sync payloads match the database schema without runtime crashes.
2. **Security Middlewares:**
   - `helmet()`: Injects secure HTTP response headers.
   - `cors()`: Allows authorized frontend clients to interact with REST endpoints.
   - `express.json({ limit: '10mb' })`: Handles bulk batch synchronization payloads.
3. **React 18 & Vite:** Ultra-fast bundling, instant hot module reload (HMR), and clean responsive UI via Tailwind CSS.

---

## Page 9: Cloud Database & Security Stack

1. **Supabase PostgreSQL 15:** ACID-compliant relational database with foreign key cascades, JSONB support, and indexing.
2. **Row Level Security (RLS):** Database engine ensures users can only read and write their own records (`auth.uid() = user_id`).
3. **Zero-Knowledge Admin Privacy Wall:** Admin panel observes server health and system throughput, but user transaction amounts and descriptions remain masked.

---

## Page 10: Android App Structure & MVVM Architecture

```
com.smarttracker/
├── data/
│   ├── local/ (AppDatabase, DAOs, Entities)
│   ├── remote/ (ApiService, RetrofitClient)
│   └── repository/ (TransactionRepository, SyncRepository)
├── ui/
│   ├── splash/ (SplashActivity.java)
│   ├── auth/ (AuthActivity.java)
│   ├── main/ (MainActivity.java)
│   ├── home/ (HomeFragment.java)
│   ├── activity/ (ActivityFragment.java)
│   ├── analytics/ (AnalyticsFragment.java)
│   ├── voice/ (VoiceBottomSheet.java)
│   └── settings/ (SettingsFragment.java)
└── worker/ (SyncWorker.java, ExpenseReminderWorker.java)
```

---

## Page 11: Room Database Entities & DAO Implementation

### `TransactionEntity.java`
```java
@Entity(tableName = "transactions")
public class TransactionEntity {
    @PrimaryKey @NonNull public String id;
    @NonNull public String userId;
    @NonNull public String accountId;
    @NonNull public String type; // "expense" | "received"
    public long amountMinor; // Stored in Paise
    public String currencyCode; // "INR"
    public String categoryId;
    public String description;
    public long transactionDate;
    public String idempotencyKey;
    public boolean isSynced;
    public long createdAt;
}
```

---

## Page 12: Voice Assistant Engine (Bilingual AI)

- **SpeechRecognizer Integration:** Captures raw audio stream from microphone.
- **Regex Intent Parser:**
  - *"500 mile save kardo"* &rarr; Amount: ₹500, Type: `received`, Category: `salary`
  - *"Chai ke 20 rupaye kharch ho gaye"* &rarr; Amount: ₹20, Type: `expense`, Category: `food`
  - *"mat karo / cancel"* &rarr; Aborts transaction and closes sheet.
- **SoundPool Audio Feedback:** Plays a crisp emerald confirmation chime upon success.

---

## Page 13: Push Notifications & Smart Back Navigation

1. **Periodic Reminders:** `ExpenseReminderWorker.java` fires every 30 minutes with customized vector icon `ic_notification_logo.xml`.
2. **Smart Back Navigation:** Pressing hardware back on non-Home tabs safely navigates back to Home tab without killing the application.
3. **Double-Back Exit:** A 2-second toast window prevents accidental app termination when on the Home tab.

---

## Page 14: Backend Server Architecture (server.ts)

Entry point runs on **Port 4000**:
- Loads environment credentials via `dotenv`.
- Mounts `/health` for heartbeat monitoring.
- Mounts `/api/v1/auth`, `/api/v1/sync`, `/api/v1/admin`, and `/api/v1/admin/monitoring`.
- Logs network activity and latency using Winston and Morgan.

---

## Page 15: REST API Endpoints Reference

| Method | Endpoint | Description |
| :---: | :--- | :--- |
| `GET` | `/health` | Server heartbeat check |
| `POST` | `/api/v1/auth/register` | New user signup in Supabase Auth |
| `POST` | `/api/v1/auth/login` | Returns JWT access token |
| `POST` | `/api/v1/sync/push` | Uploads offline transactions to cloud |
| `GET` | `/api/v1/sync/pull` | Downloads latest cloud updates to mobile |
| `GET` | `/api/v1/sync/status` | Reports sync queue status and timestamps |
| `GET` | `/api/v1/admin/overview` | System metrics and database table counts |
| `GET` | `/api/v1/admin/monitoring/summary` | Live component health and queue telemetry |

---

## Page 16: Idempotency & Sync Engine Algorithms

Network retries can duplicate financial records. Smart Expenses Tracker assigns a **UUID v4 Idempotency Key** to every transaction.
- When `/api/v1/sync/push` executes, the backend queries Supabase for `idempotency_key = payload.key`.
- If already found, the insert is skipped and an acknowledgment is returned.
- If not found, the record is inserted atomically.
- Conflict strategy: **Last-Write-Wins (LWW)** based on UTC transaction timestamp.

---

## Page 17: Supabase PostgreSQL Database Schema

Core tables in Supabase:
- `profiles`: User account metadata linked to Supabase Auth.
- `accounts`: User wallets (Cash, Bank, UPI) with `balance_minor`.
- `categories`: Standard spending categories with icons and color codes.
- `transactions`: Immutable financial ledger with foreign key links.
- `budgets`: Spending limits per category.
- `admin_audit_logs`: Audit trail of security operations.

---

## Page 18: Row Level Security (RLS) & Multi-Tenancy

Every table has RLS enabled:
```sql
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "RLS_TRANSACTIONS_OWNER_SELECT" 
ON public.transactions FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "RLS_TRANSACTIONS_OWNER_INSERT" 
ON public.transactions FOR INSERT 
WITH CHECK (auth.uid() = user_id);
```
Direct access attempts without a matching JWT token result in 0 rows or 403 Forbidden.

---

## Page 19: React Web Admin Control Panel

Accessible via **`http://localhost:5173`**:
- **Diagnostic Heartbeat Probes:** Live status of PostgreSQL, Express Relay, and JWT Auth.
- **Sync Telemetry:** Processing rate, queue backlog, and network retries.
- **Hardware Device Linking:** Displays attached Android device (Nova 1 5G, Android 14).
- **Privacy Wall:** User financial amounts remain obscured from administrative view.

---

## Page 20: Prerequisites & Environment Setup

Software required:
1. **Node.js:** v18.0.0+ LTS
2. **Java JDK:** JDK 17 (or Android Studio bundled JBR)
3. **Android Studio:** Hedgehog or higher with Android SDK 34
4. **ADB Platform Tools:** Installed in system PATH or Android SDK directory
5. **Backend `.env`:** Configured with `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `JWT_SECRET`.

---

## Page 21: Step-by-Step Running Guide: Automated (.bat Files)

### Option A: Master 1-Click Launch
Double click **`RUN_AND_INSTALL.bat`**:
1. Starts the Backend server on Port 4000.
2. Starts the React Admin panel on Port 5173.
3. Detects connected phone and installs the Android APK via ADB.

### Option B: Server Only
Double click **`START_ALL.bat`**:
- Launches backend and admin portals in separate visible terminal windows.

### Safe Shutdown
Double click **`STOP_ALL.bat`**:
- Releases Port 4000 and 5173 to prevent EADDRINUSE errors.

---

## Page 22: Step-by-Step Running Guide: Manual Terminal Commands

```bash
# Terminal 1: Backend Server
cd backend
npm install
npm run dev

# Terminal 2: Admin Control Panel
cd admin
npm install
npm run dev

# Android App:
# Open 'android' folder in Android Studio and click Run 'app' (Green Play Button).
```

---

## Page 23: Real Android Phone USB Installation (Nova 1 5G)

1. Open **Settings &rarr; About Phone** on your phone.
2. Tap **Build Number** 7 times to enable Developer Mode.
3. Open **Developer Options** and enable **USB Debugging**.
4. Connect the phone via USB cable to the PC.
5. Check phone screen and select **"Always allow from this computer"** &rarr; Tap **OK**.
6. Double click **`INSTALL_ANDROID_USB.bat`** to push and launch the APK directly on the phone.

---

## Page 24: Batch Scripts Deep Breakdown (Part 1: START & STOP)

- **`START_ALL.bat`:** Uses `start "Window Title" cmd /k` to run background services in dedicated consoles while displaying formatted endpoints.
- **`STOP_ALL.bat`:** Queries `netstat -aon | findstr :4000` to find running process PIDs and forcefully terminates them via `taskkill /F /PID`, guaranteeing clean port reuse.

---

## Page 25: Batch Scripts Deep Breakdown (Part 2: INSTALL & RUN)

- **`INSTALL_ANDROID_USB.bat`:** Searches for `adb.exe` in local SDK path or system PATH, runs `adb devices` with regex matching, triggers Gradle assembleDebug fallback if APK is missing, and starts the activity using `adb shell am start`.
- **`RUN_AND_INSTALL.bat`:** Orchestrator script that chains `START_ALL.bat` and `INSTALL_ANDROID_USB.bat` sequentially.

---

## Page 26: Offline-First Synchronization Lifecycle

1. **User saves transaction:** Instant insert into Room SQLite local DB (`isSynced = false`). UI updates in 0 milliseconds.
2. **WorkManager monitors network:** When Wi-Fi/Cellular is active, `SyncWorker` pulls unsynced records.
3. **Payload pushed to server:** Sent to `/api/v1/sync/push` with JWT credentials.
4. **Server deduplication:** Supabase records transaction and returns 200 OK.
5. **Local state updated:** Room updates `isSynced = true`.
6. **Cloud restore:** Clearing app cache and re-logging triggers `/api/v1/sync/pull` to restore historical data.

---

## Page 27: Troubleshooting: Top Common Errors & Exact Fixes

1. **`EADDRINUSE :4000`:** Run `STOP_ALL.bat` or run `npx kill-port 4000`.
2. **`device unauthorized` in ADB:** Re-plug USB cable and accept the RSA key popup on the phone screen.
3. **`CLEARTEXT communication not permitted`:** Ensure `android:usesCleartextTraffic="true"` is present in `AndroidManifest.xml`.
4. **`JAVA_HOME invalid`:** Set `JAVA_HOME` to `C:\\Program Files\\Android\\Android Studio\\jbr`.
5. **`SpeechRecognizer No Match`:** Speak clearly into the microphone in Hindi or English.

---

## Page 28: Advanced Debugging & Log Monitoring

- **Android Logcat:** Filter by `tag:SmartExpenses` to view local Room DB queries and WorkManager sync logs.
- **Express Terminal:** Monitor live HTTP requests, status codes (200 OK, 401 Unauthorized), and response latency.
- **Supabase Web Console:** Inspect live cloud rows in Table Editor at `https://supabase.com/dashboard`.

---

## Page 29: Project File Structure Directory Map

- **Root (`/`):** Batch automation files (`START_ALL.bat`, `STOP_ALL.bat`, `INSTALL_ANDROID_USB.bat`, `RUN_AND_INSTALL.bat`).
- **`android/`:** Complete Android Studio project (Java source, XML layouts, Gradle build scripts).
- **`backend/`:** Node.js Express TypeScript server and REST route controllers.
- **`admin/`:** React 18 Vite Web Control Panel source and Tailwind assets.
- **`APK/`:** Standalone installable binary (`SmartExpenses-v1.0.apk`).

---

## Page 30: University Viva & Practical Q&A

**Q1: Why Pure Java and XML instead of Kotlin / Jetpack Compose?**  
*A:* Pure Java and XML strictly align with the BCA Semester V syllabus, testing core Object-Oriented principles, Android lifecycle management, and design patterns (MVVM, DAO) without depending on Kotlin-specific runtime libraries.

**Q2: Why are monetary amounts stored as integer Paise instead of double/float?**  
*A:* Floating-point numbers under IEEE-754 introduce representation errors (e.g. 0.1 + 0.2 = 0.30000000000000004). To guarantee bank-grade accuracy, all financial values are stored in minor units (`long` in Java, `BIGINT` in PostgreSQL).

**Q3: How does the app handle offline data entry?**  
*A:* We implement a local-first architecture where data is written immediately to Room SQLite. Android Jetpack WorkManager queues unsynced records and synchronizes them with Supabase PostgreSQL as soon as internet connectivity is detected.

**Q4: How does Row Level Security protect user privacy?**  
*A:* Supabase enforces RLS at the PostgreSQL kernel level. Even if an external request reaches the database, PostgreSQL validates the caller's JWT token and restricts visibility to rows where `auth.uid() = user_id`.

---
*Official Handbook compiled for SRK Institute of Management and Computer Application, Sapeda (K.S.K.V. Kachchh University) by Asther & Divya.*
"""

root_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(root_dir, "SMART_EXPENSES_HINGLISH_MASTER_GUIDE.md")

with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"Comprehensive Markdown Handbook written successfully: {md_path}")
print(f"File Size: {os.path.getsize(md_path) / 1024:.2f} KB")
