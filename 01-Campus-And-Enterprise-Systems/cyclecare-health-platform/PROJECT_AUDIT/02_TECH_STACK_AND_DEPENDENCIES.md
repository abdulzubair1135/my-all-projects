# 02_TECH_STACK_AND_DEPENDENCIES.md — Technology Stack and Dependencies

**Scope:** Complete technical specification of languages, runtimes, frameworks, software development kits, dependencies, and build pipelines in the CycleCare project.  
**Audit Date:** 2026-10-10  
**Evidence Standard:** Strict inspection of `backend/package.json`, `android/build.gradle`, `android/app/build.gradle`, `gradle-wrapper.properties`, and runtime environment queries.

---

## 1. Programming Languages & Core Runtimes

| Technology | Declared Version | Verified Version | Purpose in Project |
| :--- | :---: | :---: | :--- |
| **Java** | 1.8 (Java 8 compatibility) | JDK 17 (Build daemon runtime) | Core language for native Android mobile application (MVVM, Activities, Adapters, DAOs). |
| **JavaScript (Node.js)** | Node >= 18.0.0 | Node v20.x (Render Linux & Local) | REST API server, business logic services, database connection pooling, admin dashboard backend. |
| **SQL (PostgreSQL dialect)** | PostgreSQL 15+ (Supabase) | PostgreSQL 15.6 | Relational data persistence, schema definitions, constraints, triggers, and migrations. |
| **HTML5 / CSS3** | Modern Standards | Rendered in Chrome/Edge/WebViews | Single-page administrative dashboard interface (`admin.html`). |
| **Python** | 3.x | Python 3.10 | Offline asset generation and transparent PNG mask processing (`make_transparent.py`). |

---

## 2. Android SDK & Build Configuration

| Property | Value | Source File | Forensic Assessment |
| :--- | :---: | :--- | :--- |
| **Application ID** | `com.cyclecare` | `android/app/build.gradle` (line 11) | Official package identifier. |
| **Compile SDK** | `34` (Android 14) | `android/app/build.gradle` (line 8) | Up to date with latest Android API levels. |
| **Min SDK** | `24` (Android 7.0 Nougat) | `android/app/build.gradle` (line 12) | Covers ~96% of active Android devices globally. |
| **Target SDK** | `34` (Android 14) | `android/app/build.gradle` (line 13) | Compliant with Google Play Store target API requirements. |
| **Version Code** | `1` | `android/app/build.gradle` (line 14) | Initial release sequence. |
| **Version Name** | `1.0.0` | `android/app/build.gradle` (line 15) | Baseline production release designation. |
| **Java Compatibility** | `JavaVersion.VERSION_1_8` | `android/app/build.gradle` (lines 35-36) | Source and target byte-code level. |
| **Gradle Wrapper** | `8.9` | `gradle/wrapper/gradle-wrapper.properties` | Current modern Gradle release. |
| **Android Gradle Plugin** | `8.2.2` | `android/build.gradle` | Compatible with Gradle 8.9 and JDK 17+. |
| **Google Services Plugin**| `4.4.0` | `android/build.gradle` | Required for Firebase Cloud Messaging integration. |

---

## 3. Android Client Dependencies (`android/app/build.gradle`)

| Dependency Coordinate | Version Declared | Role & Purpose | Where Used | Criticality |
| :--- | :---: | :--- | :--- | :---: |
| `androidx.appcompat:appcompat` | `1.6.1` | Core backwards-compatible Android UI activities | Base activities throughout app | Essential |
| `com.google.android.material:material` | `1.9.0` | Material Design 3 cards, dialogs, buttons, bottom sheets | Navigation, cards, inputs | Essential |
| `androidx.constraintlayout:constraintlayout` | `2.1.4` | Flexible, flat hierarchy layout engine | 90% of XML layouts | Essential |
| `androidx.swiperefreshlayout:swiperefreshlayout` | `1.1.0` | Pull-to-refresh container for lists and store | `fragment_store.xml`, `activity_orders.xml` | Optional |
| `androidx.cardview:cardview` | `1.0.0` | Card elevation and corner rounding containers | UI card wrappers | Essential |
| `androidx.lifecycle:lifecycle-viewmodel` | `2.6.2` | ViewModel architecture component lifecycle binding | MVVM architecture layer | Essential |
| `androidx.lifecycle:lifecycle-livedata` | `2.6.2` | Observable data holders for reactive UI updates | Repository and ViewModels | Essential |
| `androidx.room:room-runtime` | `2.5.2` | Room SQLite object-relational mapping library | Local database persistence | Essential |
| `androidx.room:room-compiler` | `2.5.2` | Java annotation processor generating DAO code | Compile-time code generation | Essential |
| `com.squareup.retrofit2:retrofit` | `2.9.0` | Type-safe REST client for HTTP networking | `ApiClient.java`, `ApiService.java` | Essential |
| `com.squareup.retrofit2:converter-gson` | `2.9.0` | JSON deserialization converter for Retrofit | API response mapping | Essential |
| `com.squareup.okhttp3:logging-interceptor` | `4.11.0` | HTTP request/response debugging logger | `ApiClient.java` | Essential |
| `androidx.work:work-runtime` | `2.8.1` | Background deferrable task manager for offline sync | `SyncWorker.java` | Essential |
| `androidx.biometric:biometric` | `1.1.0` | Fingerprint and face biometric authentication | Privacy lock before viewing logs | Essential |
| `androidx.security:security-crypto` | `1.1.0-alpha06`| EncryptedSharedPreferences for token storage | Secure session management | Essential |
| `com.google.firebase:firebase-bom` | `32.8.0` | Bill of Materials for Firebase library consistency | Gradle dependency resolver | Essential |
| `com.google.firebase:firebase-messaging` | (BOM-managed) | Push notifications receiver for cycle alerts | `CycleCareMessagingService.java` | Essential |
| `com.google.android.gms:play-services-maps` | `18.2.0` | Google Maps SDK for courier location rendering | `OrderTrackingActivity.java` | Essential |
| `com.google.android.gms:play-services-location` | `21.2.0` | Fused Location Provider for auto-detecting address | `AddressManagementActivity.java` | Essential |
| `com.razorpay:checkout` | `1.6.33` | Razorpay Android mobile checkout interface | `CheckoutActivity.java` | Essential |
| `junit:junit` | `4.13.2` | Java unit testing framework | Unit tests | Testing |
| `androidx.test.ext:junit` | `1.1.5` | Android instrumentation test extensions | Android tests | Testing |
| `androidx.test.espresso:espresso-core` | `3.5.1` | Automated UI interaction testing | UI tests | Testing |

---

## 4. Backend Dependencies (`backend/package.json`)

| Package Name | Version Declared | Purpose & Usage in Code | Criticality |
| :--- | :---: | :--- | :---: |
| `express` | `^4.18.2` | Core HTTP REST application framework (`app.js`) | Essential |
| `pg` | `^8.23.1` | PostgreSQL client and connection pooling engine (`db.js`, `supabase.js`) | Essential |
| `@supabase/supabase-js` | `^2.39.0` | Supabase JavaScript client library | Secondary / Fallback |
| `bcryptjs` | `^2.4.3` | Password hashing and comparison (`authController.js`) | Essential |
| `jsonwebtoken` | `^9.0.2` | Signed JWT generation and verification (`auth.js`, `authController.js`) | Essential |
| `helmet` | `^7.1.0` | Security headers middleware (CSP, XSS, Frameguard) (`app.js`) | Essential |
| `cors` | `^2.8.5` | Cross-Origin Resource Sharing middleware (`app.js`) | Essential |
| `morgan` | `^1.10.0` | HTTP request logging middleware (`app.js`) | Operational |
| `dotenv` | `^16.3.1` | Environment variable loader from `.env` (`server.js`, `db.js`) | Essential |
| `express-rate-limit` | `^7.1.5` | IP-based rate limiter (200 requests / 15 min window) (`app.js`) | Essential |
| `razorpay` | `^2.9.2` | Server-side Razorpay order creation and signature validation | Essential |
| `jest` | `^29.7.0` | Backend test runner and assertion framework (`devDependencies`) | Testing |
| `supertest` | `^6.3.3` | HTTP API integration test library (`devDependencies`) | Testing |
| `nodemon` | `^3.0.2` | Development automatic file reload daemon (`devDependencies`) | Development |

---

## 5. External Services & Cloud Architecture

1. **Supabase Cloud (PostgreSQL 15.6):**
   - Host: `aws-0-ap-southeast-2.pooler.supabase.com:6543`
   - Pooling Mode: Transaction-safe pooler with 15-second connect timeout.
2. **Render Cloud:**
   - Web Service: `srv-db2dehflk1mc73b14sbg`
   - Domain: `https://cyclecare-57my.onrender.com`
   - Auto-deploy: Triggered on Git push to branch `main`.
3. **Firebase Cloud Messaging:**
   - Project: CycleCare Mobile
   - Push Channels: Discreet cycle reminders, partner alerts, delivery updates.
4. **Razorpay Payments:**
   - Standard Indian payment gateway supporting UPI, Cards, NetBanking, and Wallets.
   - Verified via concrete fallback DemoPaymentProvider for offline/demo simulations.
