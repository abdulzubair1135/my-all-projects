# 10_DEMO_MOCK_AND_REAL_DATA.md — Demo, Mock, and Real Data Systems

**Scope:** Forensic inventory and analysis of seed accounts, demo personas, mock payment providers, telemetry simulators, and real database classification rules in CycleCare.  
**Audit Date:** 2026-10-10  
**Evidence Standard:** PostgreSQL seed scripts (`backend/scripts/*.js`), migrations, controller flags, and live database query records.

---

## 1. Real vs. Demo Data Classification Rules

The CycleCare backend establishes an explicit boundary between production/organic data and demo/testing data:

1. **User Classification (`users.account_type`):**
   - Value `'REAL'`: Created through organic registration (`RegisterActivity.java` or `POST /api/v1/auth/register`). Real consumer account.
   - Value `'DEMO'`: Created via seed scripts (`seedDemoAccounts.js`, `seedAmanAccount.js`) or with known demo domain suffixes (`@cyclecare.app`, `@cyclecare.com`).
2. **Order Classification (`orders.order_type`):**
   - Value `'REAL'`: Placed by real users with real product selections. Displayed in green pills in `admin.html`.
   - Value `'DEMO'`: Placed using the demo payment flow or created via demo seed routines (e.g. order `#CC-DEMO-1001`). Displayed in slate gray pills.
3. **Database Segregation Policy:**
   - Both real and demo records reside in the authoritative Supabase PostgreSQL database to ensure that queries, indexes, and foreign keys execute under authentic database constraints.
   - Demo records never overwrite or cross-contaminate real customer accounts or order metrics.

---

## 2. Seed Accounts Inventory

| Email Address | Role | Display Name | Gender | Account Type | Account Tag | Seed Script / Source | Purpose |
| :--- | :---: | :--- | :---: | :---: | :--- | :--- | :--- |
| `demo@cyclecare.com` | `USER` | Aastha Sharma (Girl) | FEMALE | `DEMO` | `REAL USER` | `seedDemoAccounts.js` | Primary demo tracker persona for testing cycle dial and period logging |
| `aman.husband@cyclecare.app` | `USER` | Aman Sharma (Husband) | MALE | `DEMO` | `REAL USER` | `seedAmanAccount.js` | Partner care persona linked to demo user for testing chat & gifting |
| `husband.demo@cyclecare.app` | `USER` | Rahul Sharma (Husband) | MALE | `DEMO` | `REAL USER` | `seedDemoAccounts.js` | Secondary partner persona |
| `delivery.demo@cyclecare.app` | `USER` | CycleCare Demo Courier | MALE | `DEMO` | `REAL USER` | `seedDemoAccounts.js` | Dedicated courier persona for testing dispatch & OTP verification |
| `admin@cyclecare.app` | `ADMIN` | CycleCare Admin | FEMALE | `DEMO` | `REAL USER` | `seedDemoAccounts.js` | Administrative account for verifying role-based web control panel |
| `newuser@cyclecare.com` | `USER` | Demo User | FEMALE | `DEMO` | `REAL USER` | `001_initial_schema.sql` | Baseline seed user associated with demo order `#CC-DEMO-1001` |

### Verified Real Organic Accounts in Database:
- `abdulzubair221@gmail.com` (Display Name: `dream`, Role: `USER`, `account_type: 'REAL'`, Tag: `REAL USER`)
- `organic.user.112502@gmail.com` (Display Name: `Priya VIP 112502`, Role: `USER`, `account_type: 'REAL'`, Tag: `VIP ORGANIC MEMBER`)
- `organic.user.219532@gmail.com` (Display Name: `Priya VIP 219532`, Role: `USER`, `account_type: 'REAL'`, Tag: `VIP ORGANIC MEMBER`)

---

## 3. Demo Orders & Simulated Telemetry

### 3.1 Demo Order `#CC-DEMO-1001`
- **Location in Code:** `backend/src/controllers/deliveryController.js:240` (`resetDemoDelivery`).
- **Initial State:** `order_status = 'READY_FOR_DELIVERY'`, `delivery_status = 'READY_FOR_DELIVERY'`, `payment_status = 'SUCCESS'`.
- **Items:** CycleCare Care Kit (Subtotal: ₹368.00).
- **Delivery OTP:** `4821` (Fixed demo OTP for verification).
- **Reset Capability:** The Admin Panel and Android client expose a 1-tap reset endpoint (`POST /api/v1/deliveries/demo/reset`) that resets this demo order and delivery state without affecting real customer purchases.

### 3.2 Telemetry GPS Simulator
- **Implementation:** `backend/src/controllers/deliveryController.js` (`simulateLocation`).
- **Mechanism:** Computes linear interpolation between warehouse coordinates (Latitude: `19.0760`, Longitude: `72.8777` - Mumbai) and destination coordinates (Latitude: `19.1136`, Longitude: `72.8697`).
- **Progress Steps:** `25%` (ETA 20 min), `50%` (ETA 15 min), `75%` (ETA 10 min), `90%` (ETA 3 min), `100%` (Arrived).
- **Storage:** Persisted to `delivery_live_locations` table so that real-time polling or WebSocket listeners reflect continuous motion.

---

## 4. Payment Gateway Mocks vs. Real Providers

| Component | Provider / Implementation | Where Defined | Behavior |
| :--- | :--- | :--- | :--- |
| **Razorpay Gateway** | Real SDK (Sandbox / Test Mode) | `backend/src/config/razorpay.js`, `CheckoutActivity.java` | Initiates real order on Razorpay servers; generates genuine `order_id`; verifies HMAC signature. |
| **DemoPaymentProvider** | Abstract Interface Implementation | `backend/src/services/paymentProvider.js`, `paymentsController.js` | 1-tap payment settlement for automated test suites and instant demonstration. Updates order to `PAID` and decrements real inventory. |

---

## 5. Mock vs. Dynamic Data in UI Screens

1. **Eliminated Hardcoded Data:**
   - The former static *"4 days left"* fallback in `HomeFragment.java` has been upgraded to dynamic calculation based on real period records in SQLite Room DB and PostgreSQL.
   - The Admin dashboard formerly had static summary cards; it now executes raw parameterized SQL queries (`COUNT(DISTINCT users.id)`, `SUM(total_amount)`) against PostgreSQL.
2. **Current Dynamic Flow:**
   - Dynamic period estimation calculates exact remaining days based on real dates.
   - Product catalog prices, stock numbers, images, and descriptions load dynamically from the database.
   - User followers and following lists query the authoritative `user_follows` table.
