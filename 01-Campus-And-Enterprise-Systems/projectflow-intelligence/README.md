# ProjectFlow Intelligence — Enterprise Full-Stack System

[![System Status](https://img.shields.io/badge/System_Status-ONLINE-success.svg)](https://projectflow-intelligence.onrender.com)
[![Cloud Server](https://img.shields.io/badge/Host-Render_Cloud-46E3B7.svg)](https://projectflow-intelligence.onrender.com)
[![Database](https://img.shields.io/badge/Database-Supabase_PostgreSQL-3ECF8E.svg)](https://loqiqdgnjgozeixepfkk.supabase.co)
[![Notifications](https://img.shields.io/badge/Push_Alerts-Firebase_FCM-FFCA28.svg)](https://firebase.google.com)
[![Mobile App](https://img.shields.io/badge/Client-Android_Native_v2.0.0-3DDC84.svg)](releases/android/ProjectFlow-Intelligence-v2.0.0.apk)

ProjectFlow Intelligence is an enterprise-grade, offline-first project intelligence and operations platform. It combines a **Node.js/Express full-stack backend**, a **React/Tailwind web administration console**, a native **Android client application** with an organic Natural Mineral / Limestone design aesthetic, **Supabase PostgreSQL** cloud persistence, and **Firebase Cloud Messaging (FCM)** real-time push dispatching.

---

## 🏗️ 1. Complete Architecture Overview

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │            WEB ADMIN CONTROL PANEL (React)             │
                                  │       https://projectflow-intelligence.onrender.com    │
                                  └───────────┬────────────────────────────────┬───────────┘
                                              │                                │
                                              ▼                                ▼
                          ┌───────────────────────────────────────┐  ┌──────────────────────────────────────┐
                          │         RENDER CLOUD (REST API)       │  │          SUPABASE (Database)         │
                          │   - Express.js Engine (Node.js)       │  │   - PostgreSQL Database Engine       │
                          │   - Stateless JWT Authentication      │  │   - Profiles, Workspaces & Projects  │
                          │   - Deterministic Risk Radar Engine   │  │   - Real-time Tasks & Kanban state   │
                          │   - APK Delivery Gateway              │  │   - WhatsApp-Style Messages & DMs    │
                          │   - Audit Telemetry Logger            │  │   - Tamper-Evident Audit Records     │
                          └───────────────────┬───────────────────┘  └──────────────────────────────────────┘
                                              │
                                              ▼
                          ┌───────────────────────────────────────┐
                          │        FIREBASE (Push Engine)         │
                          │   - Google FCM Cloud Messaging        │
                          │   - Task Assign & Status Notifications│
                          │   - Real-time Chat Heads-up Alerts    │
                          └───────────────────┬───────────────────┘
                                              │
                                              ▼
                                  ┌───────────────────────────────────────┐
                                  │          ANDROID MOBILE APP           │
                                  │    - Offline-First Room Database      │
                                  │    - Background WorkManager Sync      │
                                  │    - Warm Limestone Natural Theme     │
                                  └───────────────────────────────────────┘
```

---

## ⚡ 2. 1-Click Master Control File (`PROJECTFLOW.bat`)

All redundant batch scripts have been unified into a single master file in the repository root:
👉 **[`PROJECTFLOW.bat`](file:///c:/Users/abdul/OneDrive/ドキュメント/puneet/PROJECTFLOW.bat)**

Double-clicking `PROJECTFLOW.bat` launches an interactive console:
```text
======================================================================
             PROJECTFLOW INTELLIGENCE - MASTER CONSOLE
======================================================================

  [1] Start Website & Full-Stack Server (Opens http://localhost:8082)
  [2] Open Live Render Cloud Website (https://projectflow-intelligence.onrender.com)
  [3] Compile & Install Android App on Phone (ADB)
  [4] Stop / Close All Running Services
  [5] Check System Health & Database Status
  [6] Exit Console

======================================================================
Enter your choice (1-6) [Default: 1]:
```

* **Option 1**: Starts the local Node server and automatically launches your browser to the Web Admin Panel.
* **Option 2**: Directly opens the live Render production website.
* **Option 3**: Compiles the Android APK via Gradle and installs it directly on a connected physical phone via ADB.
* **Option 4**: Gracefully stops all local background Node and Web server processes.
* **Option 5**: Performs live connectivity probes to Render, Supabase, and ADB.

---

## 🌐 3. Live Environments & URLs

| Component | Target URL / Host | Purpose |
|---|---|---|
| **Production Web Panel** | [https://projectflow-intelligence.onrender.com](https://projectflow-intelligence.onrender.com) | Live Web Admin Console |
| **REST API Base URL** | `https://projectflow-intelligence.onrender.com/api/v1/` | Universal Client Gateway |
| **Local Web Server** | `http://localhost:8082` | Local pair-programming environment |
| **Cloud Database** | `https://loqiqdgnjgozeixepfkk.supabase.co` | Supabase Cloud PostgreSQL |
| **Android APK Release** | [`releases/android/ProjectFlow-Intelligence-v2.0.0.apk`](releases/android/ProjectFlow-Intelligence-v2.0.0.apk) | Universal signed binary (8.11 MB) |

---

## 🔐 4. Default Credentials (Zero Demo Data)

All accounts are persisted in Supabase `profiles` with bcrypt/JWT cryptographic protection:

| Role | Email Address | Default Password | Access Level |
|---|---|---|---|
| **System Administrator** | `admin@projectflow.io` | `ProjectFlow@2026` | Full Tenant & RBAC Authority |
| **Project Manager** | `manager@projectflow.io` | `ProjectFlow@2026` | Project & Task Management |
| **Team Member** | `member@projectflow.io` | `ProjectFlow@2026` | Standard Task Contributor |
| **Registered User** | `abdulzubair221@gmail.com` | `ProjectFlow@2026` | Platform Member |

---

## 📱 5. Android Mobile Application Features

The native Android app (`com.projectflow.android`) features:
1. **Natural Mineral / Limestone Design**: Warm `#F3EDE2` canvas, high-contrast typography, and soft terracotta accents (`@color/earth_bg`, `@color/limestone_card`).
2. **WhatsApp-Style Chat**:
   - 1-on-1 Direct Personal Chats (clicking any member under Team opens their private room).
   - Squad Group Channels (`#general`, `#engineering`, `#design-squad`) created exclusively by Administrators.
   - 3-Dots Contact Inspector dialog showing real email, global role, 🟢 Online / ⚪ Offline badge, and assigned tasks.
3. **Live Online / Offline Heartbeat**: Real active session tracking via `/api/v1/users/heartbeat`. No false green dots.
4. **Offline-First Synchronization**: Room SQLite cache with background WorkManager `SyncWorker` queue.
5. **Firebase Push Notifications (FCM)**: Immediate heads-up system tray banners for task delegations, risk alerts, and chats.

---

## 💻 6. Web Admin Console Features

1. **Dashboard & Velocity Metrics**: Live completion rate radar, 3D project progress ring, and overdue velocity tracking.
2. **Projects Explorer**: Interactive project status dropdowns, target baseline deadline dates, and Supabase database synchronization.
3. **Tasks Explorer (Kanban & Table)**:
   - 4-Lane Kanban board (`To Do`, `In Progress`, `Review`, `Done`).
   - Inline status transitions with automated progress calculation.
   - Squad group assignment and priority tagging (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
4. **Deterministic Risk Radar**:
   - 6 mathematical rule evaluations (overdue tasks, missing assignees, deadline slippages, capacity bottlenecks).
   - Live "Acknowledge & Mitigate" resolution actions.
5. **WhatsApp-Style Discussions**: Dual-pane conversation manager with channel browser, direct chat threads, and message composer.
6. **Push Broadcast Portal**: Direct FCM push notification dispatcher with delivery receipt logs.
7. **User Directory & RBAC**: Real-time user accounts, 🟢 online badges, role editor modal (`ADMINISTRATOR`, `MANAGER`, `MEMBER`, `VIEWER`), and account deactivate/reactivate toggle.
8. **App Releases & APK Portal**: Version tracking, SHA-256 integrity checksum verification, and direct APK streaming.
9. **Security Audit Logging**: Comprehensive audit trail capturing all system events with JSON inspector and one-click **Export to CSV** and **Export to JSON**.
10. **Enterprise System Settings**: Persisted configuration for sync cadence, batch mutation limits, FCM gateway toggles, and risk thresholds.

---

## 🛠️ 7. Development & Deployment Commands

### Backend & Web Build
```bash
# Build production web bundle
cd admin-panel
npm install
npm run build

# Start production server locally
cd ..
node server.js
```

### Android APK Build
```bash
# Compile Android debug APK (safe for OneDrive paths)
.\gradlew.bat assembleDebug -PbuildDir=C:/temp/projectflow_build

# Install directly to attached device via ADB
adb -s <DEVICE_ID> install -r C:/temp/projectflow_build/android-app/outputs/apk/debug/android-app-debug.apk
```

### Render Deployment
Deployment on Render is fully automated. Pushing commits to the `main` branch triggers the Render build pipeline defined in [`render.yaml`](render.yaml):
```bash
git add -A
git commit -m "feat: updates"
git push origin main
```
Render automatically builds the Vite frontend and executes `node server.js`.

---

## 📄 8. Documentation Sitemap

Deep-dive documentation is located in the [`docs/`](docs/) directory:
- [API Integration Guide](docs/API_INTEGRATION.md) — Endpoint contracts and payload formats.
- [Database Schema](docs/DATABASE_SCHEMA.md) — Supabase PostgreSQL schema and migration scripts.
- [Security & RBAC](docs/SECURITY_AND_RBAC.md) — Role permissions and tenant isolation rules.
- [Deterministic Risk Radar](docs/RISK_RADAR_SPECIFICATION.md) — Algorithms and mathematical telemetry.
- [Offline Sync Protocol](docs/OFFLINE_SYNC_PROTOCOL.md) — Room queue reconciliation and conflict resolution.
- [Design System](docs/DESIGN_SYSTEM_NATURAL_MINERAL.md) — Natural Mineral palette specification and style guide.
