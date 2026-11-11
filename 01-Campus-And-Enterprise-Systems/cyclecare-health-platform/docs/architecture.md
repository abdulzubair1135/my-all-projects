# CycleCare System Architecture Document

## Overview
CycleCare is a privacy-focused menstrual wellness and period-care Android application supported by a Node.js/Express REST backend, Supabase PostgreSQL database, and an Admin Management System.

## Architecture Diagram
```
+-------------------------------------------------------------+
|                     Android Application                     |
|  - Native Java (com.cyclecare)                              |
|  - MVVM Architecture + Room Offline Caching                 |
|  - WorkManager Sync + Biometric Security + Retrofit API     |
+-------------------------------------------------------------+
                              |
                     HTTPS (REST API v1)
                              v
+-------------------------------------------------------------+
|                  Render Node.js Backend API                 |
|  - Express REST Router & Controllers                        |
|  - JWT Auth + RBAC Middleware (USER, ADMIN, SUPER_ADMIN)    |
|  - Razorpay Payment Verification & Webhook Endpoint        |
|  - Admin Dashboard Web Engine                               |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                    Supabase PostgreSQL                      |
|  - Row Level Security (RLS) Enabled                         |
|  - Normalized Schemas & Relational Integrity                |
|  - Supabase Storage (Product & Content Images)              |
+-------------------------------------------------------------+
```

## Android App Layer Architecture
- **Language:** Java (Android SDK)
- **Design Pattern:** Model-View-ViewModel (MVVM)
- **Database / Cache:** Room Persistence Library for offline-first cycle/symptom/mood tracking
- **Networking:** Retrofit 2 + OkHttp 4 with Auth Interceptor and JSON serialization
- **State Management:** LiveData & ViewModel
- **Background Sync:** WorkManager (`SyncWorker`) for syncing offline actions when connected
- **Security:** EncryptedSharedPreferences, BiometricPrompt API, App Lock PIN

## Node.js Backend Layer Architecture
- **Environment:** Node.js + Express.js
- **Routing:** `/api/v1` scoped REST routes
- **Security Middleware:** Helmet, CORS, Rate-Limiter, JWT bearer auth handler, RBAC checker
- **Payment Gateway Integration:** Server-side order creation, HMAC-SHA256 signature verification, and webhook handling
- **Admin Panel:** Built-in web administration interface for catalog, inventory, order processing, and user access management

## Database Architecture
- **Engine:** PostgreSQL hosted on Supabase
- **Authentication & Authorization:** JWT token validation and RLS enforcement per user
- **Migrations:** Sequential SQL migration files in `database/migrations/`
