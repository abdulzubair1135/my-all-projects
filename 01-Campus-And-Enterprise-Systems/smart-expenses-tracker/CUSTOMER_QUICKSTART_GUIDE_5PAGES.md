# 📱 Smart Expenses Tracker - Customer QuickStart Guide (5 Pages)

> **Official GitHub Repository:** [https://github.com/smartexpensehelp-sketch](https://github.com/smartexpensehelp-sketch)  
> **Customer Delivery Archive:** `SmartExpenses-Complete-Project.zip`  
> **Architecture:** Pure Java 17 + XML (Android) | Node.js Express (Relay) | React Vite (Admin) | Supabase PostgreSQL 15 (Cloud)  

---

## 📄 Page 1: 1-Click Fast Start: Pura App & Server Kaise Chalu Karein

Aapko kisi complex command ki zaroorat nahi hai. Folder me ready-made `.bat` automation scripts hain:

### Step 1: Server & Admin Website Chalu Karein
- Folder me ja kar **`START_ALL.bat`** par double click karein.
- Yeh do background windows open karega:
  1. **Backend API Relay:** `http://localhost:4000` (Health Check: `http://localhost:4000/health`)
  2. **Admin Web Portal:** `http://localhost:5173`

### Step 2: Phone Me App Install Karein
- Phone ko USB cable se computer se connect karein.
- Folder me ja kar **`INSTALL_ANDROID_USB.bat`** par double click karein.
- App compile hokar phone screen par direct launch ho jayega!

### Step 3: Server Safely Band Kaise Karein?
- Hamesha **`STOP_ALL.bat`** par double-click karein taaki background ports (4000 & 5173) clean ho sakein.

---

## 📄 Page 2: GitHub & Folder Structure: Kidar Kya Hai?

GitHub Link: **[https://github.com/smartexpensehelp-sketch](https://github.com/smartexpensehelp-sketch)**

| Folder / File | Category | Iska Kaam Kya Hai? |
| :--- | :--- | :--- |
| **`android/`** | Android Mobile App | Pure Java 17 aur XML layouts ka complete Android Studio project (Room DB, Voice Engine, UI). |
| **`backend/`** | Backend Relay Server | Node.js Express TypeScript server (Port 4000) jo mobile aur database ke beech bridge hai. |
| **`admin/`** | Web Admin Portal | React 18 + Vite Admin Console (Port 5173) telemetry aur component diagnostics ke liye. |
| **`APK/`** | Pre-compiled Binary | `SmartExpenses-v1.0.apk` jo bina Android Studio khole direct install ho sakti hai. |
| **`*.bat files`** | Desktop Automation | `START_ALL.bat`, `STOP_ALL.bat`, `INSTALL_ANDROID_USB.bat`, `RUN_AND_INSTALL.bat`. |

*Note: Android project me 0% Kotlin hai, complete Pure Java & XML architecture hai.*

---

## 📄 Page 3: Supabase Cloud Database & Backend Setup

### Supabase Kya Hai?
Supabase ek enterprise-grade cloud **PostgreSQL 15** database hai jaha phone ka sara financial data encrypt hokar permanently store hota hai.
- **Row Level Security (RLS):** Ek user ka data doosre user se 100% isolated rehta hai.
- **Paise Precision:** Amount `amount_minor BIGINT` me store hota hai (₹500.00 = `50000` Paise), jisse koi rounding bug nahi aata.

### Live Database Kaise Check Karein?
1. Open karein: [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Project select karein (`dymorpzwrmvfpubgsgqb`).
3. Left menu me **Table Editor** par click karein.
4. Tables check karein: `transactions`, `profiles`, `accounts`.

### Backend `.env` Keys:
Backend ke `backend/.env` file me keys pehle se configured hain. `START_ALL.bat` chalate hi backend automatically database se connect ho jata hai!

---

## 📄 Page 4: Android Studio Me Project Kaise Open Karein

> ⚠️ **Important:** Android Studio me poora folder select mat karein! Hamesha sirf **`android`** folder ko select karein.

1. **Android Studio Open Karein:** Welcome screen par **Open** (ya **File &rarr; Open**) par click karein.
2. **Path Select Karein:** `.../divya/android` folder select karke **OK** dabayein.
3. **Gradle Sync:** 1-2 minute wait karein jab tak neeche status bar me *Gradle sync finished* na aa jaye.
4. **JDK Check:** Settings &rarr; Build Tools &rarr; Gradle me **Embedded JDK 17** ya **Android Studio JBR** select hona chahiye.
5. **Run 'app':** Device select karein aur Green **Play Button** (Run) par click karein.

---

## 📄 Page 5: Real Phone Me USB Debugging & Network Setup

Physical Android phone (jaise **Nova 1 5G**) par app chalane ka tarika:

### 1. Phone Me Developer Mode On Karein:
- **Settings &rarr; About Phone** me jayein.
- **Build Number** par lagataar **7 baar tap karein**. Message aayega: *"You are now a developer!"*.

### 2. USB Debugging Enable Karein:
- **Settings &rarr; Additional Settings &rarr; Developer Options** me jayein.
- **USB Debugging** ON karein.
- USB cable lagayein aur phone screen par **"Always allow from this computer"** tick karke **OK** karein.

### 3. 1-Click Install:
- Folder me **`INSTALL_ANDROID_USB.bat`** par double click karein. App phone me direct open ho jayegi!

### 4. Local Server vs Cloud Sync:
Phone me app by default cloud Render API (`https://smart-expenses-kuob.onrender.com`) par sync hoti hai, isliye phone kisi bhi normal internet (Wi-Fi ya Mobile Data) par ho, sync 100% seamless kaam karta hai!

---
*Customer QuickStart Documentation generated for Smart Expenses Tracker.*
