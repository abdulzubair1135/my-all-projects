# CYCLECARE — FORENSIC EVIDENCE & REFERENCES INDEX
## Source File Registry, Git Commits, Asset Mapping & Cryptographic Proofs

---

## 1. SOURCE CODE FORENSIC FILE REGISTRY (सोर्स कोड प्रमाण सूची)

CycleCare project ka har technical claim directly codebase ke physical files aur lines se back kiya gaya hai:

| File Relative Path | Primary Language / Type | Size (Bytes) | Forensic Role & Key Implementation |
| :--- | :--- | :---: | :--- |
| `backend/src/server.js` | JavaScript (Node.js) | ~1,200 | HTTP process bootstrap, port binding, and graceful shutdown. |
| `backend/src/app.js` | JavaScript (Express) | ~3,400 | Middlewares (Helmet, CORS, Morgan), static admin view mount, API routes. |
| `backend/src/config/db.js` | JavaScript | ~1,500 | Dual DNS fallback (`8.8.8.8`, `1.1.1.1`) + pg Pool configuration. |
| `backend/src/services/relationshipMappingService.js` | JavaScript | ~2,100 | Bi-directional reciprocal relationship logic (Husband/Wife, Father/Child). |
| `backend/src/controllers/partnerController.js` | JavaScript | ~6,800 | Reciprocal tagging endpoint, permissions toggle, partner dashboard serializer. |
| `backend/src/controllers/deliveryController.js` | JavaScript | ~7,900 | Delivery agent dashboard, OTP verification, live courier simulation. |
| `backend/src/controllers/ordersController.js` | JavaScript | ~5,600 | ACID transaction order placement, item insertion, delivery generation. |
| `backend/src/controllers/cycleController.js` | JavaScript | ~4,800 | Period log insertion, heuristic cycle phase prediction calculations. |
| `backend/src/views/admin.html` | HTML5 / CSS3 / JS | ~16,400 | Single-Page Web Admin Control Panel with telemetry and dispatch tables. |
| `backend/tests/reciprocal_relationship.test.js`| JavaScript (Jest) | ~14,200 | 27 automated test cases for reciprocal relationship tagging. |
| `backend/tests/partner_family_sharing.test.js` | JavaScript (Jest) | ~11,800 | 19 automated test cases for invites and granular permissions. |
| `android/app/src/main/AndroidManifest.xml` | XML | ~3,200 | App permissions, deep links (`cyclecare://*`), and Activity declarations. |
| `android/app/src/main/java/com/cyclecare/auth/LoginActivity.java` | Java | ~5,400 | Login logic, Panda mascot animation binding, demo courier button. |
| `android/app/src/main/java/com/cyclecare/partner/DeliveryAgentActivity.java`| Java | ~6,200 | Courier agent dashboard, step stepper, 4-digit OTP prompt dialog. |
| `android/app/src/main/java/com/cyclecare/partner/OrderTrackingActivity.java`| Java | ~5,800 | Live customer route stepper, secret OTP display (`4821`). |
| `android/app/src/main/java/com/cyclecare/partner/RelationshipTagDialogFragment.java`| Java | ~4,200 | Reciprocal tag selector dialog with live preview. |
| `database/migrations/005_trusted_circle_and_delivery.sql` | SQL | ~3,800 | Delivery columns, OTP fields, and tracking events table. |
| `database/migrations/006_reciprocal_relationships.sql` | SQL | ~4,100 | Reciprocal tag column and `sharing_audit_events` audit table. |

---

## 2. GIT COMMIT EVIDENCE LOG (गिट कमिट रिकॉर्ड्स)

Git version control repository ka verified forensic history:

- **Repository Origin URL:** `https://github.com/cyclecarehelpcenter-sudo/CycleCare.git`
- **Active Branch:** `main`
- **Recent Forensic Commits:**
  - `0200cde`: `feat(partner): implement automatic reciprocal relationship tagging system with bidirectional sync, Jest test suite, and Android UI preview`
  - `79ec191`: `fix(ui): restore Panda mascot transparency in dark mode and fix profile text contrast`
  - `6955a5b`: `feat(delivery): complete end-to-end delivery agent mode with live OTP verification and courier privacy isolation`
  - `482a17f`: `fix(db): implement dual DNS fallback for Supabase connection pooler`

---

## 3. ASSET INVENTORY & SCREENSHOT INDEX (एसेट्स सूची)

Folder: `CYCLECARE_COMPLETE_DOCUMENTATION/assets/`

| Asset Filename | Format & Dimensions | Associated Screen / Component |
| :--- | :--- | :--- |
| `mascot_idle.png` | PNG (Transparent Alpha) | Default relaxed companion pose |
| `mascot_blink.png` | PNG (Transparent Alpha) | Animated blinking companion pose |
| `mascot_wave.png` | PNG (Transparent Alpha) | Waving friendly greeting pose |
| `mascot_shy.png` | PNG (Transparent Alpha) | Shy / eye-covering companion pose |
| `screen_login.png` | PNG (1080x2400) | Login Activity with demo courier login |
| `screen_home_dashboard.png` | PNG (1080x2400) | Home Dashboard with circular cycle dial |
| `screen_cycle_calendar.png` | PNG (1080x2400) | Monthly Cycle Grid Calendar view |
| `screen_period_log_modal.png` | PNG (1080x2400) | Period Logging Modal with flow & cramp chips |
| `screen_wellness_store.png` | PNG (1080x2400) | Wellness E-Commerce Store catalog |
| `screen_product_detail.png` | PNG (1080x2400) | Product Detail Activity with safety badges |
| `screen_order_dialog.png` | PNG (1080x2400) | Checkout Summary Dialog & payment modes |
| `screen_order_success.png` | PNG (1080x2400) | Order Placed celebration with waving panda |
| `screen_order_tracking.png` | PNG (1080x2400) | Live Route Map Tracking & Secret OTP banner |
| `screen_partner_dashboard.png`| PNG (1080x2400) | Partner Care Dashboard with reciprocal tag |
| `screen_relationship_tag_modal.png`| PNG (1080x2400) | Reciprocal Relationship Tagging Dialog |
| `screen_conversations_inbox.png`| PNG (1080x2400) | Trusted Circle Conversations Inbox |
| `screen_chat_messages.png` | PNG (1080x2400) | Real-time chat messages stream |
| `screen_chat_care_items.png` | PNG (1080x2400) | Care Hamper Gifting BottomSheet in chat |
| `screen_sharing_permissions.png`| PNG (1080x2400)| Granular Privacy Sharing switches |
| `screen_profile_view.png` | PNG (1080x2400) | User Profile view with stats & cycle settings |
| `screen_profile_dark_mode.png` | PNG (1080x2400) | Profile in Dark Mode (High-contrast verified) |
| `screen_social_followers.png` | PNG (1080x2400) | Social Community Followers BottomSheet |
| `screen_admin_panel.png` | PNG (1280x900) | Admin Web Control Panel live browser view |
