# CYCLECARE — MASTER PRODUCTION APP & BACKEND

> **Tagline:** Track • Understand • Prepare • Care  
> **Central Idea:** *"CycleCare doesn't just track your period. It helps you prepare for it."*

CycleCare is a privacy-focused menstrual wellness, period-tracking, and care preparation Android application supported by a Node.js/Express REST backend, Supabase PostgreSQL database, and an Admin Management System.

---

## 📑 Table of Contents
1. [Product Overview & Key Features](#1-product-overview--key-features)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [Project Directory Structure](#4-project-directory-structure)
5. [Database Schema & Migrations](#5-database-schema--migrations)
6. [Backend Setup & Environment Variables](#6-backend-setup--environment-variables)
7. [Android Application Setup & Release Build](#7-android-application-setup--release-build)
8. [API Endpoints Summary](#8-api-endpoints-summary)
9. [Web Admin Management Panel](#9-web-admin-management-panel)
10. [Offline-First & Synchronization](#10-offline-first--synchronization)
11. [Security & Privacy Controls](#11-security--privacy-controls)
12. [Testing & Verification](#12-testing--verification)

---

## 1. Product Overview & Key Features

CycleCare is engineered around preparation and user privacy:

- 🩸 **Period Tracking & Flow Logging:** Start/end dates, flow intensity (`LIGHT`, `MEDIUM`, `HEAVY`), notes. Validation prevents duplicate/overlapping entries or end dates before start dates.
- 📅 **Monthly Period Calendar:** View period windows, symptoms, moods, and upcoming events.
- 🔮 **Period Estimation:** Calculated baseline estimates using historical cycle averages with clear disclaimers that prediction is an *estimate*, not a medical diagnosis.
- 🎒 **Prepare Mode & Custom Care Kits:** Dedicated workflow when period approaches to prepare period essentials, heating pads, dark chocolate, and care kits.
- 🚨 **Emergency Mode:** One-tap quick-access checklist for unexpected period starts.
- 🛍️ **Integrated Comfort Store:** E-commerce for period care, comfort, personal hygiene, and dark chocolate snacks with server-side price validation and stock control.
- 🛒 **Cart, Checkout & Razorpay Integration:** Server-side HMAC signature verification (`POST /payments/verify`) and webhook processing.
- 🔄 **Buy Again & Restock Tracker:** Re-add valid available stock items from prior orders and set restocking alert thresholds.
- 🤖 **Educational AI Assistant ("Ask CycleCare"):** General wellness Q&A that does not diagnose or prescribe. Cycle history data sharing requires explicit user permission per prompt.
- 🔒 **Privacy & Security:** App lock PIN/Biometrics, discreet notification mode, data export (JSON), and complete account deletion.

---

## 2. Technology Stack

### Android Client
- **Language:** Java (Native Android)
- **UI:** XML Layouts, Material Design 3 Components, Custom Cards & Views
- **Architecture:** MVVM (Model-View-ViewModel) + Repository Pattern + LiveData
- **Local Cache:** Room Persistence Library (`AppDatabase`)
- **Networking:** Retrofit 2 + OkHttp 4 with `AuthInterceptor`
- **Background Sync:** WorkManager (`SyncWorker`)
- **Security:** EncryptedSharedPreferences, BiometricPrompt API

### Backend Server
- **Runtime:** Node.js + Express.js
- **Hosting Target:** Render
- **Security:** Helmet, CORS, Express-Rate-Limit, JWT Bearer Token Auth, RBAC Middleware
- **Payments:** Razorpay Server-Side Order & HMAC Verification SDK

### Database & Storage
- **Database Engine:** Supabase PostgreSQL
- **Security:** Row Level Security (RLS) policies
- **File Storage:** Supabase Storage (Product & Article imagery)

---

## 3. System Architecture

```
Android Java Application (com.cyclecare)
        │
      HTTPS (REST API v1)
        ▼
Render Node.js Backend API
  ├─ JWT Authorization & RBAC Middleware
  ├─ Razorpay Server-Side HMAC Verification
  └─ Web Admin Dashboard (/admin-panel)
        │
        ▼
Supabase PostgreSQL & Storage
  ├─ Row-Level Security (RLS)
  └─ Normalized Relational Schema
```

---

## 4. Project Directory Structure

```
arti astha/
├── .env.example                       # Environment variables template
├── README.md                          # Master documentation
├── database/
│   └── migrations/
│       ├── 001_initial_schema.sql     # Core Supabase PostgreSQL tables & indexes
│       └── 002_rls_policies_and_seed.sql # RLS policies & initial seed data
├── docs/
│   ├── architecture.md               # Architecture details & diagrams
│   ├── database.md                   # Data dictionary & schemas
│   ├── api.md                        # Complete REST API specification
│   ├── security.md                   # Security & Privacy rules
│   └── deployment.md                 # Deployment & Release instructions
├── backend/
│   ├── package.json
│   ├── tests/
│   │   └── api.test.js               # Integration test suite
│   └── src/
│       ├── app.js                    # Express app configuration
│       ├── server.js                 # Server entry point
│       ├── config/                   # Supabase & Razorpay clients
│       ├── middleware/               # Auth JWT, RBAC, Error Handler
│       ├── controllers/              # Auth, Cycle, Symptoms, Store, Orders, Admin...
│       ├── routes/                   # REST API routes
│       ├── services/                 # Cycle Math & Payment verification services
│       └── views/
│           └── admin.html            # Web Admin Dashboard UI
└── android/                          # Gradle Android Java Application
    ├── build.gradle
    ├── settings.gradle
    └── app/
        ├── build.gradle
        ├── proguard-rules.pro
        └── src/main/
            ├── AndroidManifest.xml
            ├── java/com/cyclecare/   # Java MVVM source code
            └── res/                  # XML Layouts, Values, Colors, Menus
```

---

## 5. Database Schema & Migrations

Execute the migration scripts in Supabase SQL Editor in order:
1. `database/migrations/001_initial_schema.sql` (Creates `users`, `profiles`, `cycle_settings`, `period_logs`, `symptoms`, `moods`, `categories`, `products`, `orders`, `payments`, `care_kits`, `user_product_tracking`, `wellness_articles`, `ai_conversations`, `audit_logs`).
2. `database/migrations/002_rls_policies_and_seed.sql` (Enforces Row Level Security and seeds default symptoms, moods, product categories, products, and wellness articles).

---

## 6. Backend Setup & Environment Variables

1. Navigate to the backend directory:
   ```bash
   cd backend
   npm install
   ```
2. Copy `.env.example` to `.env` and fill in your keys:
   ```env
   PORT=5000
   NODE_ENV=development
   JWT_SECRET=your_jwt_secret_key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   RAZORPAY_KEY_ID=rzp_test_key_id
   RAZORPAY_KEY_SECRET=your_razorpay_secret
   ```
3. Start the server:
   - Development: `npm run dev`
   - Production / Render: `npm start`
4. Run Integration Tests:
   ```bash
   npm test
   ```

---

## 7. Android Application Setup & Release Build

1. Open the `android` folder in **Android Studio**.
2. Synchronize Gradle project files.
3. Configure target server URL in `android/app/build.gradle`:
   - Debug: `http://10.0.2.2:5000/api/v1/` (Local Emulator)
   - Release: `https://cyclecare-api.onrender.com/api/v1/`
4. Build Debug APK: Select **Build -> Build Bundle(s) / APK(s) -> Build APK(s)**.
5. Generate Release Signed APK: Select **Build -> Generate Signed Bundle / APK**.

---

## 8. API Endpoints Summary

- **AUTH:** `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- **CYCLE:** `GET /api/v1/cycle`, `POST /api/v1/cycle/period`, `PATCH /api/v1/cycle/period/:id`, `DELETE /api/v1/cycle/period/:id`, `GET /api/v1/cycle/prediction`, `GET /api/v1/cycle/insights`
- **SYMPTOMS & MOODS:** `GET /api/v1/symptoms`, `POST /api/v1/symptoms/log`, `GET /api/v1/moods`, `POST /api/v1/moods/log`
- **STORE & CART:** `GET /api/v1/store/products`, `GET /api/v1/store/cart`, `POST /api/v1/store/cart/items`, `DELETE /api/v1/store/cart/items/:id`
- **ORDERS & PAYMENTS:** `POST /api/v1/orders`, `GET /api/v1/orders`, `POST /api/v1/payments/create`, `POST /api/v1/payments/verify`
- **CARE KITS:** `GET /api/v1/care-kits`, `POST /api/v1/care-kits`, `POST /api/v1/care-kits/:id/buy`, `GET /api/v1/care-kits/budget-calculator`
- **AI ASSISTANT:** `POST /api/v1/ai/chat`
- **ADMIN:** `GET /api/v1/admin/dashboard`, `GET /api/v1/admin/users`, `GET /api/v1/admin/products`, `GET /api/v1/admin/orders`, `GET /api/v1/admin/audit-logs`

---

## 9. Web Admin Management Panel

Admins and Super Admins can access the web dashboard via:
`http://localhost:5000/admin-panel/admin.html` (or deployed URL).

Features include real-time metrics (total users, total orders, revenue), low-stock inventory alerts, order status transitions (`PENDING` ➔ `PAID` ➔ `SHIPPED` ➔ `DELIVERED`), user management, and system audit logs.

---

## 10. Offline-First & Synchronization

The Android app features complete offline functionality for cycle tracking:
- Log period entries, symptoms, and moods while offline using **Room Database** (`AppDatabase`).
- Pending logs are queued in `sync_queue`.
- **WorkManager (`SyncWorker`)** automatically pushes queued items to the Node.js API server when an internet connection becomes available.

---

## 11. Security & Privacy Controls

- **Zero Client Secrets:** Production secrets, DB passwords, and payment private keys are kept strictly in backend environment variables.
- **Server-Side Financial Security:** All price calculations, discounts, inventory deductions, and Razorpay HMAC signature validations occur server-side.
- **Discreet Notifications:** Users can enable discreet notification mode so alerts read "CycleCare: You have a reminder" without exposing private period details on lock screens.
- **Data Privacy & Erasure:** Users retain complete control with one-click JSON data export and account deletion endpoints.

---

## 12. Testing & Verification

Run backend integration and security test assertions:
```bash
cd backend && npm test
```

All security requirements (unauthorized route blocking, RBAC role boundaries, server-side payment verification, price tamper resistance) have been tested and verified.
