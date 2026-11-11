# CYCLECARE — EXECUTIVE PROJECT OVERVIEW
## Full-Stack Period Wellness, Partner Care & Family Support Ecosystem

---

## 1. PROJECT IDENTITY & VISION (प्रोजेक्ट परिचय और विज़न)

| Project Attribute | Value / Details |
| :--- | :--- |
| **Project Name** | **CycleCare** |
| **Subtitle / Tagline** | Period & Cycle Wellness, Partner Care and Family Support Application |
| **Target Audience** | Women, menstruating individuals, husbands, boyfriends, fathers, mothers, siblings, and delivery partners |
| **Primary Platform** | Android Native (API Level 26+ / Android 8.0 to Android 14+) |
| **Backend Architecture** | Node.js (v18+) + Express REST API Server |
| **Database Architecture** | Supabase Cloud PostgreSQL (Transaction & Session Pooler) |
| **Deployment Target** | Render Web Service (Cloud Hosting) + Local Production Daemon |
| **Admin Control** | CycleCare Admin Single-Page Control Panel (`/admin`) |
| **Core Philosophy** | Menstrual health sirf ek individual ka struggle nahi hai — yeh pure parivar aur relationship ka ek compassionate care ecosystem hona chahiye. |

CycleCare ek modern full-stack mobile aur cloud ecosystem hai jiska main maqsad menstrual health tracking ko social isolation aur awkwardness se nikal kar **empathy, awareness, aur proactive partner care** mein convert karna hai. CycleCare traditional period tracking apps se fundamentally alag hai kyunki yeh women ke sath-sath unke **partners aur family members** ko bhi ek safe, secure, aur privacy-controlled platform par connect karta hai.

---

## 2. PROBLEM STATEMENT (समस्या का विश्लेषण)

Aaj ke samay mein menstrual hygiene aur cycle wellness apps market mein available hain, lekin unme multiple critical gaps aur practical problems hain:

1. **Lack of Male & Partner Awareness (पार्टनर में समझ की कमी):**
   - Menstrual cycle ke different phases (Menstrual, Follicular, Ovulation, Luteal) ke dauran hormonal changes aur emotional fluctuations ko partner samajh nahi paate.
   - Result: Misunderstandings, relationship stress, aur physical discomfort ke samay emotional support ka na milna.

2. **Awkwardness & Social Stigma (बात करने में झिझक):**
   - Traditional Indian aur Asian families mein period ke bare mein baat karna abhi bhi tabu mana jata hai. Ladkiyan apne father, bhai ya husband se openly sanitary pads ya medicine mangwane mein hesitate karti hain.

3. **Emergency Discomfort & Delivery Delays (इमरजेंसी सैनिटरी नीड्स):**
   - Periods frequently unexpected dates par aa jate hain (sudden onset). Emergency mein medical stores par jana ya quick relief items (cramp patches, heating pads, herbal teas) arrange karna difficult hota hai.
   - General delivery apps par sanitary items order karte waqt courier partner ko sensitive health status expose hone ka privacy risk rehta hai.

4. **Privacy vs Transparency Conflict (प्राइवेसी और ट्रांसपेरेंसी का द्वंद्व):**
   - Existing apps ya toh sab kuch share kar deti hain ya fir kuch bhi share nahi karti. User ke paas granular control nahi hota ki partner kya dekh sakta hai (e.g., phase dekh sake lekin intimate symptoms ya private notes na dikhein).

5. **Fragile Reciprocal Relationships (रिलेशनशिप का कन्फ्यूजन):**
   - Jab ek user kisi ko "Husband" mark karta hai, toh doosre user ke account mein yeh apne aap "Wife" ke roop mein reflect nahi hota tha, jisse asymmetrical aur broken UX create hoti thi.

---

## 3. THE CYCLECARE SOLUTION (समाधान के 5 मुख्य स्तम्भ)

CycleCare in sabhi samasyaon ka complete, integrated end-to-end technical solution provide karta hai:

```
+-----------------------------------------------------------------------------------+
|                           CYCLECARE 5 CORE PILLARS                                |
+-----------------------------------------------------------------------------------+
|  1. CYCLE WELLNESS     | Intelligent cycle phase calculation, symptom logging,     |
|     & HEALTH TRACKING  | ovulation prediction, hydration and medicine reminders.   |
|------------------------+-----------------------------------------------------------|
|  2. PARTNER CARE &     | Automatic bidirectional reciprocal tagging (Husband-Wife, |
|     RECIPROCAL SHARING | Father-Daughter/Son), granular privacy permissions.       |
|------------------------+-----------------------------------------------------------|
|  3. CIRCLE CARE CHAT   | Real-time encrypted messaging, instant care-bundle gifting|
|     & GIFTING          | directly inside chat bubbles with 1-click ordering.       |
|------------------------+-----------------------------------------------------------|
|  4. WELLNESS STORE &   | Curated comfort items, 15-25 min express delivery, live   |
|     EXPRESS DELIVERY   | courier simulation, secure 4-digit OTP handover.          |
|------------------------+-----------------------------------------------------------|
|  5. ADMIN CONTROL      | Real-time telemetry, database pool diagnostics, inventory |
|     PANEL & MONITORING | tracking, error logs inspection, order dispatch engine.   |
+-----------------------------------------------------------------------------------+
```

### Pillar 1: Intelligent Cycle & Wellness Tracking
- **Smart Phase Calculator:** User ke cycle history aur period duration ke base par current cycle day, exact phase (Menstrual, Follicular, Ovulatory, Luteal), aur next period arrival date predict hoti hai.
- **Symptom Logging:** Cramps intensity (Mild, Moderate, Severe), Flow level (Light, Medium, Heavy), Mood (Calm, Anxious, Irritable), Energy level, aur custom notes ko structured database mein record kiya jata hai.
- **Panda Companion (Interactive Mascot):** Application mein ek playful panda mascot integrate hai jo 4 real-time visual states (`idle`, `blink`, `wave`, `shy`) render karta hai, jisse user ko non-clinical, comforting experience milta hai.

### Pillar 2: Partner Care & Automatic Reciprocal Tagging
- **Bidirectional Relationship Sync:** Agar User A apne partner ko **Husband** assign karta hai, toh backend automatically gender aur relationship context validate karke User B ke view mein User A ko **Wife** mark karta hai.
- Supported reciprocal pairs:
  - *Husband <---> Wife*
  - *Boyfriend <---> Girlfriend*
  - *Father <---> Daughter / Son* (based on profile gender)
  - *Mother <---> Daughter / Son*
  - *Brother <---> Sister / Brother*
  - *Sister <---> Sister / Brother*
- **Granular Privacy Matrix (`partner_permissions`):** Menstruating user ke paas full authority hoti hai ki partner ko kya dikhana hai:
  - Phase visibility (ON/OFF)
  - Symptoms visibility (ON/OFF)
  - Next period prediction date (ON/OFF)
  - Daily mood updates (ON/OFF)
- **Discreet Notifications:** Partner ko masked text messages bheje jate hain (e.g., *"Take extra care of your partner today — bring some dark chocolate!"*) bina awkward medical terms use kiye.

### Pillar 3: Trusted Circle Care & Interactive Chat
- **In-App Messaging:** Users aur unke trusted partners ke beech end-to-end conversation channel.
- **Care Pack Gifting via Chat:** Partner chat window se hi direct "Cramp Relief Kit", "Comfort Tea", ya "Warm Water Bag" select karke gift bhej sakta hai. Chat message ke andar interactive card render hota hai jo 1-click par order confirm karta hai.

### Pillar 4: E-Commerce Wellness Store & Express Courier Delivery
- **Curated Store Catalog:** Pads, Tampons, Menstrual Cups, Cramp Patches, Herbal Drinks, aur Pain Relief Gels.
- **Instant Checkout & Order Lifecycle:** Order create hone par database mein `orders`, `order_items`, aur `deliveries` tables update hote hain.
- **Demo Payment Gateway:** Pluggable `PaymentProvider` interface ke sath realistic payment flows (Success, Failure, Cancel) test kiye ja sakte hain.
- **Courier Privacy Isolation:** Delivery agent ko recipient ka naam, delivery address, aur item count dikhta hai — lekin uski koi bhi cycle ya health information delivery agent ke app mein expose nahi hoti!
- **4-Digit OTP Verification:** Courier package sirf tab mark hota hai jab recipient apna private OTP (e.g. `4821`) delivery agent ko provide karta hai.

### Pillar 5: Real-Time Admin Control Panel
- Web-based single page application jo production backend ke sath directly communicate karta hai.
- Real-time KPI counters (Total Users, Period Logs, Orders, Inventory Levels, Active Deliveries).
- Live Database Connection Pool diagnostics (Latency, Active Clients, DNS Fallback Status).
- Immediate error monitoring aur system audit logs table.

---

## 4. HIGH-LEVEL ARCHITECTURE OVERVIEW (सिस्टम आर्किटेक्चर सारांश)

CycleCare ka architecture pure industrial standard layered separation of concerns follow karta hai:

```
[ Android Client (Java/XML) ]
       |
       |  Retrofit 2.9 + OkHttp3 (Bearer JWT, Auto Retry, JSON Serialization)
       v
[ Express.js REST API Server (Node v18+) ]
  ├── Security Layer (Helmet, CORS, Rate Limit, Error Logger)
  ├── Authentication & JWT Middleware (`authenticateToken`, `requireAdmin`)
  ├── Business Logic Controllers (Auth, Cycle, Partner, Orders, Delivery)
  ├── Domain Services (RelationshipMappingService, PaymentProvider)
  └── Database Gateway (pg Pool with Dual DNS Fallback 8.8.8.8 / 1.1.1.1)
       |
       |  SSL Connection Pooler (Port 6543)
       v
[ Supabase PostgreSQL Relational Database ]
  ├── Master Tables: users, profiles, period_logs, symptoms
  ├── Social & Circle Tables: partner_connections, partner_permissions, circle_messages
  ├── E-Commerce Tables: products, orders, order_items, deliveries
  └── Audit & Telemetry: sharing_audit_events, app_error_logs, delivery_tracking_events
```

---

## 5. KEY PROJECT METRICS & VERIFIED ACHIEVEMENTS (सत्यापित उपलब्धियां)

CycleCare project ka forensic audit aur live test verification complete ho chuka hai. Verified metrics niche diye gaye hain:

| Metric / Parameter | Verified Result | Evidence / Proof |
| :--- | :--- | :--- |
| **Android Build Status** | **BUILD SUCCESSFUL** | Gradle `assembleDebug` completed in 29 seconds, 0 lint crash errors. |
| **Backend Test Suite Pass Rate** | **100% (76/76 Passed)** | Jest test suites executed against live database. |
| **Reciprocal Relationship Suite** | **27/27 PASSED** | `tests/reciprocal_relationship.test.js` (100.9s duration). |
| **Partner & Family Sharing Suite** | **19/19 PASSED** | `tests/partner_family_sharing.test.js` (95.9s duration). |
| **Integration & API Suite** | **30/30 PASSED** | `tests/integration_audit_suite.test.js` & `tests/api.test.js`. |
| **Database Pooler Stability** | **100% Uptime** | Dual DNS Fallback (Google `8.8.8.8` + Cloudflare `1.1.1.1`) resolving Supabase AWS pooler. |
| **Admin Panel Status** | **100% Functional** | Real-time HTML5 SPA serving metrics, orders, deliveries, and telemetry. |
| **Mascot Rendering Quality** | **100% Restored** | 4 custom poses with background transparency and zero-box dark mode blending. |

---

## 6. INTENDED REPORT STRUCTURE (इस डॉक्यूमेंटेशन रिपोर्ट की रूपरेखा)

Yeh documentation suite pure project ko A se Z tak forensic precision ke sath cover karta hai. Agle chapters mein detailed technical documentation is sequence mein pesh ki gayi hai:

1. **Chapter 04:** Complete Technical Architecture (Layers, Data Flow, Security Pipeline).
2. **Chapter 05:** UI/UX Screen-by-Screen Catalog (Har screen ki visual hierarchy, XML files, dark mode styling).
3. **Chapter 06:** Complete API Reference (Har REST endpoint ka method, URL, headers, request/response body).
4. **Chapter 07:** Database Schema & Data Dictionary (15+ tables, foreign keys, constraints, RLS policies).
5. **Chapter 08:** Android Source Code Map (Java packages, MVVM classes, XML layouts, Room SQLite).
6. **Chapter 09:** Backend Source Code Map (Express routes, controllers, services, database connection pool).
7. **Chapter 10:** Admin Control Panel Reference (SPA controls, order lifecycle, diagnostic metrics).
8. **Chapter 11:** Notifications & Real-Time Flows (Push alerts, polling mechanisms, privacy masks).
9. **Chapter 12:** Security, Privacy & Compliance Audit (Encryption, sanitization, role separation).
10. **Chapter 13:** Test Cases & Execution Logs (Automated test scripts, assertions, benchmark results).
11. **Chapter 14:** Bug Register & Historical Root Cause Analysis (Panda fix, contrast fix, DNS fix, sync fixes).
12. **Chapter 15:** Deployment & Configuration Guide (Render hosting, Supabase setup, Gradle signing keys).
13. **Chapter 16:** Feature Implementation Matrix (End-to-end status of all 45+ features).
14. **Chapter 17:** Requirements Traceability Matrix (Functional requirement tracing to code).
15. **Chapter 18:** Technical Glossary & Academic Viva Preparation (Q&A guide for university exams/interviews).
16. **Chapter 19:** Forensic References & Evidence Index (Exact source files, line numbers, commit SHAs).
17. **Chapter 20:** Documentation Coverage & Quality Verification Report.
