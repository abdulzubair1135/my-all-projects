========================================================================================
     PROJECTFLOW INTELLIGENCE v2.0 - DUSRE LAPTOP ME SETUP KARNE KI COMPLETE GUIDE
========================================================================================

Bhai, is ZIP file me ProjectFlow ka sab kuch shamil hai:
1. Complete Website (React + Tailwind CSS + Lucide Icons)
2. Complete Backend (Node.js Express + Supabase Cloud Database + Presence & FCM)
3. Complete Android Application (Native Java + Room SQLite Cache-First + Neumorphic UI)
4. Production APK File (releases/android/ProjectFlow-Intelligence-v2.0.0.apk)
5. Full Documentation, API Specs & Architecture Reports (docs/, reports/, Master PDF)
6. SMART AUTO-INSTALLER .bat Scripts (jo chiz missing hogi, khud download & install karega!)

----------------------------------------------------------------------------------------
STEP-BY-STEP SETUP GUIDE (DUSRE LAPTOP ME KAISE RUN KAREIN):
----------------------------------------------------------------------------------------

[STEP 1] ZIP FILE KO EXTRACT KAREIN:
- Is ZIP file ko kisi bhi folder me extract karein (Jaise: Desktop par ya C:\ProjectFlow me).

[STEP 2] SMART ONE-CLICK AUTO INSTALLER:
- Folder me jaake seedha "1_SETUP_NEW_LAPTOP.bat" par DOUBLE CLICK karein!
- Ye script:
  * Check karega ki Node.js installed hai ya nahi.
  * AGAR NODE.JS NAHI HAI: To script use AUTOMATICALLY DOWNLOAD & SILENTLY INSTALL kar dega!
  * Saari Backend dependencies (node_modules) check & install karega.
  * Web Frontend production build check karega.
  * .env Cloud Database configuration check karega.
  * Aapko kuch bhi manually karne ki zaroorat nahi hai!

[STEP 3] WEBSITE & SERVER START KARNA:
- Simply "2_START_PROJECTFLOW.bat" par DOUBLE CLICK karein!
- Ye background me Node.js Server (Port 8082) start karega aur aapke browser me 
  URL: http://localhost:8082 automatically khol dega!

- Live Cloud Render Website (Bina laptop ke bhi online chalti hai):
  URL: https://projectflow-intelligence.onrender.com

[STEP 4] LOGIN DETAILS (DEFAULT PASSWORDS):
----------------------------------------------------------------------------------------
Role                 Email                          Password
----------------------------------------------------------------------------------------
Administrator:       admin@projectflow.io           ProjectFlow@2026
Project Manager:     manager@projectflow.io         ProjectFlow@2026
Developer / Engineer:abdulzubair221@gmail.com       kalyani
Team Member:         vipra@projectflow.io           ProjectFlow@2026
Designer:            boyundertheaim@gmail.com       ProjectFlow@2026
----------------------------------------------------------------------------------------

[STEP 5] ANDROID APP KAISE RUN KAREIN:
Option A (Direct Install via Phone):
- Phone ko USB cable se connect karein aur ye ready APK file phone me bhej dein:
  Folder: releases/android/ProjectFlow-Intelligence-v2.0.0.apk
- Phone me File Manager se APK par tap karein aur "Install" dabayein.

Option B (1-Click ADB Install):
- Phone ko USB Debugging on karke connect karein.
- "3_INSTALL_APK_TO_PHONE.bat" par double click karein, ye app install karke launch kar dega!

Option C (Android Studio Source Code):
- Agar Android code edit karna ho, to Android Studio open karein aur seedha 
  "android-app" folder ko open project karein (JDK 17 recommend hai).

[STEP 6] SERVICES BAND KARNA:
- Jab band karna ho, to "STOP_ALL_SERVICES.bat" par double click karein.

----------------------------------------------------------------------------------------
IMPORTANT FILES & FOLDER STRUCTURE:
----------------------------------------------------------------------------------------
* 1_SETUP_NEW_LAPTOP.bat      -> Smart Auto-Installer (Missing cheezein khud install karta hai)
* 2_START_PROJECTFLOW.bat     -> 1-Click Server & Web Launcher
* 3_INSTALL_APK_TO_PHONE.bat  -> 1-Click Android APK Installer to phone
* STOP_ALL_SERVICES.bat       -> Stops all ports and servers
* PROJECTFLOW.bat             -> Master interactive console menu
* server.js                   -> Main Node.js Express server
* src/                        -> Backend routes, controllers, middleware, Supabase integration
* admin-panel/                -> Web UI source code (Vite + React) & pre-built dist/
* android-app/                -> Full Native Android source code
* releases/android/           -> Pre-compiled ready-to-use Android APK v2.0.0
* docs/                       -> Architectural documentation & diagrams
* reports/                    -> Master Architecture Report PDF (Device Test & System Design)
* database/                   -> Supabase SQL schema migrations & user credentials
========================================================================================
