# 15_HANDOVER_AND_NEXT_STEPS.md — Project Handover, Critical Knowledge, and Roadmap

**Scope:** Senior engineering handover guide, non-negotiable architectural constraints, answers to the 15 fundamental project questions, and recommended continuation roadmap for CycleCare.  
**Audit Date:** 2026-10-10  
**Evidence Standard:** Full codebase synthesis, verified database status, and test execution history.

---

## 1. The 15 Fundamental Project Facts

### 1. What has actually been built?
A full-stack reproductive health platform comprising:
- Native Android application (Java 8, MVVM, Room SQLite, Material Design 3).
- REST API server in Node.js (Express 4) with 17 controllers and 68 endpoints.
- Authoritative PostgreSQL database (52 tables on Supabase cloud pooler).
- Cloud deployment on Render Linux Web Service (`https://cyclecare-57my.onrender.com`).
- Single-page administrative web control panel (`/admin-panel/admin.html`).

### 2. What genuinely works?
- **Authentication:** Registration with gender, login, JWT issuance, bcrypt hashing, demo logins, forgot password OTP `1234`.
- **Mascot Animations:** Panda idle blinking, waving on email focus, covering eyes on password focus.
- **Menstrual Cycle Tracking:** Date selection via DatePickerDialog, flow logging, local Room persistence, dynamic cycle dial calculations.
- **Trusted Circle Messaging:** WhatsApp-style conversation list, real-time message sending/deletion, care kit item sharing, custom relationship tags (`HUSBAND`, `DOCTOR`).
- **Store & Cart:** Product catalog, search, quantity steppers, shipping addresses, GPS auto-detect, demo payment provider.
- **Delivery & Tracking:** Live telemetry simulation, courier workflow dashboard, 4-digit OTP verification (`4821`).
- **Admin Control Panel:** Live KPI metrics, real vs demo segregation, inventory adjustments, orders fulfillment, chat monitoring.

### 3. What only looks finished?
- The Google Map in `OrderTrackingActivity.java`: While the UI map container, marker logic, and progress bar are fully implemented, map tiles will render blank on devices without an active Google Maps API key in `local.properties`.
- Razorpay live card transactions: Mobile checkout UI is fully connected, but sandbox test credentials are used rather than live production merchant accounts.

### 4. What uses demo or mock data?
- The preset demo login personas (`demo@cyclecare.com`, `aman.husband@cyclecare.app`, `delivery.demo@cyclecare.app`, `admin@cyclecare.app`).
- The demo payment provider (`POST /api/v1/payments/demo/success`).
- The fixed delivery OTP `4821` on demo order `#CC-DEMO-1001`.
- The demo forgot password reset OTP `1234`.
- The courier route telemetry simulator (`POST /api/v1/deliveries/:id/simulate`).

### 5. What is connected to the database?
- All user registrations, logins, profiles, and relationship tags.
- All menstrual cycle flow logs and user settings.
- All store products, stock counts, and inventory movements.
- All customer orders, order items, and shipping addresses.
- All delivery dispatches, live location coordinates, and delivery events.
- All Trusted Circle messages and social follower linkages.

### 6. What is not connected?
- Live external SMS gateway (uses demo OTP `1234` instead of cellular SMS delivery).
- Live Razorpay settlement webhook to a real bank account.

### 7. Which APIs are broken or unverified?
- **Zero broken APIs:** All 68 endpoints are operational; the previous `ReferenceError: getQuickCareItems is not defined` startup crash was resolved in commit `bc39bcd`.
- All 17 automated integration test suites and 9 unit tests pass 100%.

### 8. Which database tables are central?
1. `users` & `profiles`: Identity, role, gender, and custom relationship tags.
2. `period_logs` & `cycle_settings`: Menstrual cycle tracking and phase estimation.
3. `products` & `inventory_movements`: Catalog inventory and audit trail.
4. `orders` & `order_items`: Commerce purchases, addresses, and fulfillment status.
5. `deliveries` & `delivery_live_locations`: Courier dispatches and GPS telemetry.
6. `circle_messages`: Trusted Circle multi-user communications and shared care items.

### 9. Which features are incomplete?
- In-depth cycle chart export (PDF generation).
- Multi-currency store support (currently locked to Indian Rupee ₹).

### 10. What prevents the application from being production-ready?
1. Production environment variable secrets (replacing default `ADMIN_SECRET_KEY` and `JWT_SECRET`).
2. Google Cloud Maps API key configuration for production map tile rendering.
3. Real SMS gateway provider integration for production password resets.
4. Production Razorpay merchant account keys.

### 11. What is the biggest technical risk?
- PostgREST API Gateway rate limits: Mitigated by the direct Supabase PostgreSQL connection pooler (`pg.Pool`), which must remain the primary database access path.

### 12. What should be fixed first?
- Ensure environment variable secrets are configured in Render dashboard before public launch.

### 13. What should not be changed casually?
- **Panda Mascot Animations:** Do NOT touch `LoginActivity.java` animation handlers or asset drawables.
- **Short Path Convention for Gradle on Windows:** Always compile Android using `C:\Users\abdul\OneDrive\9831~1\ARTIAS~1\android`.
- **Database Column Names:** Note that `addresses` uses `address_line` and `pincode`; `period_logs` uses `flow`; `inventory_movements` uses `movement_type`.

### 14. What must be tested after any major change?
1. Run `npm test` in `backend/` to verify all 26 test suites pass.
2. Run `cmd /c "cd /d C:\Users\abdul\OneDrive\9831~1\ARTIAS~1\android && gradlew.bat assembleDebug"` to verify zero compilation errors.
3. Execute `curl -i https://cyclecare-57my.onrender.com/api/v1/health` to confirm cloud health.

### 15. What information is still missing?
- Production Google Cloud Maps API Key.
- Production Razorpay Merchant Credentials.

---

## 2. Recommended Engineering Roadmap for Next Sprints

### Sprint 1: Production Hardening
- Provision production Google Cloud Console project and configure Maps SDK API key.
- Rotate `ADMIN_SECRET_KEY` and `JWT_SECRET` in Render Environment dashboard.
- Link an SMS Gateway (e.g., Twilio or AWS SNS) to `authController.forgotPassword`.

### Sprint 2: Feature Enhancements
- Add period cycle PDF health summary export in `ProfileFragment`.
- Add push notification sound configuration for discreet cycle reminders.
- Add multi-language string extensions for additional regional languages (Marathi, Tamil, Telugu).
