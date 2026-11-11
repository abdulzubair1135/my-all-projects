# CYCLECARE — ADMIN CONTROL PANEL REFERENCE
## Web Dashboard Architecture, Real-Time Telemetry, Order Dispatch & Diagnostics

---

## 1. ADMIN CONTROL PANEL OVERVIEW (प्रशासन नियंत्रण कक्ष अवलोकन)

CycleCare Admin Control Panel ek high-performance, single-page web management dashboard hai jo application administrators aur operations team ko real-time visibility aur system controls provide karta hai.

- **File Path:** `backend/src/views/admin.html`
- **Access Route:** `http://localhost:5000/admin` (Local) / `https://cyclecare-backend.onrender.com/admin` (Cloud)
- **Visual Capture:** `assets/screen_admin_panel.png`
- **Underlying Stack:** Vanilla HTML5, Modern CSS3 (CSS Grid & Flexbox, Neumorphic Dark Theme), Pure JavaScript (Fetch API).
- **Zero Framework Bloat:** React ya Angular ki tarah kisi heavy build step ki requirement nahi hai — yeh direct static Express view ke roop mein instantly render hota hai.

```
+-----------------------------------------------------------------------------------+
|                        ADMIN CONTROL PANEL VISUAL LAYOUT                          |
+-----------------------------------------------------------------------------------+
| [CycleCare Logo]  CycleCare Control Panel v1.0   | Server: ACTIVE | DB: CONNECTED |
+-----------------------------------------------------------------------------------+
|  [ TOTAL USERS ]   [ PERIOD LOGS ]   [ TOTAL ORDERS ]   [ ACTIVE DELIVERIES ]     |
|      1,284              4,920              312                   4                |
+-----------------------------------------------------------------------------------+
|  [ SYSTEM DIAGNOSTICS & CONTROLS ]                                                |
|  - [ Run Diagnostic Self-Test ]      - [ Reset Demo Order #CC-DEMO-1001 ]         |
|  - [ Simulate Courier Route ]        - [ Flush Redis / Memory Cache ]             |
+-----------------------------------------------------------------------------------+
|  [ LIVE ORDERS & DISPATCH MONITORING ]                                            |
|  Order ID    | Customer      | Items        | Status          | OTP    | Action   |
|  #CC-1001    | Aastha Sharma | Wellness Kit | OUT_FOR_DELIVERY| 4821   | [Track]  |
+-----------------------------------------------------------------------------------+
|  [ LIVE SYSTEM LOGS & TELEMETRY STREAM ]                                          |
|  [INFO] DB Pool latency: 38ms | [INFO] Reciprocal tag Wife->Husband synced        |
+-----------------------------------------------------------------------------------+
```

---

## 2. CORE DASHBOARD MODULES & CONTROLS (मुख्य मॉड्यूल और कंट्रोल्स)

### Module 1: Live KPI Telemetry Cards (लाइव मैट्रिक्स)
Real-time counters jo `/api/v1/admin/stats` aur `/api/v1/monitoring/metrics` se har 10 seconds mein poll hote hain:
1. **Total Registered Users:** Application mein registered female, partner, aur delivery accounts ki total count.
2. **Total Period Logs Recorded:** Menstrual history database records ka total count.
3. **Completed Orders:** E-commerce store se fulfill ho chuke orders ki count.
4. **Active Deliveries In-Transit:** Currently transit mein chal rahe express courier orders.
5. **Database Pool Latency:** Supabase AWS pooler ke sath active ping latency (typically 35ms – 65ms).

---

### Module 2: System Diagnostics & Operations Console (ऑपरेशन्स कंसोल)
One-click administrative action buttons jo live system operations trigger karte hain:
- **`[ Run Diagnostic Self-Test ]`**: Ek sath auth database, cycle engine, delivery pipeline, aur DNS resolver ki health check run karta hai aur panel par status report print karta hai.
- **`[ Reset Demo Order #CC-DEMO-1001 ]`**: Predefined test order ko reset karke `READY_FOR_DELIVERY` state aur OTP `4821` par le aata hai, jisse evaluator ya developer live delivery demo dobara test kar sake.
- **`[ Simulate Courier Route ]`**: Assigned delivery agent ke transit coordinates ko step-by-step progress karwata hai (0% -> 25% -> 50% -> 75% -> 90% -> 100%).
- **`[ Flush Server Cache ]`**: In-memory volatile cached items aur session locks ko instantly clear karta hai.

---

### Module 3: Live Order Fulfillment & Dispatch Table (ऑर्डर एवं डिलीवरी तालिका)
Interactive table displaying all active and completed customer orders:
- **Columns Displayed:**
  - Order Number (e.g. `#CC-DEMO-1001`)
  - Recipient Name & Phone
  - Delivery Destination Address
  - Package Summary (Masked for privacy)
  - Current Status Badge (`PENDING`, `PAID`, `OUT_FOR_DELIVERY`, `DELIVERED`)
  - Delivery OTP Status (`PENDING VERIFICATION` / `VERIFIED`)
  - Action Trigger (`[View Details]`, `[Cancel Order]`, `[Force Complete]`)

---

### Module 4: Inventory Management & Stock Adjustment (इन्वेंटरी कंट्रोल)
Store catalog ke physical inventory levels ko inspect aur adjust karne ka interface:
- Har product ke live stock levels display hote hain.
- Low-stock threshold warning (< 10 units par amber alert highlight).
- Admin panel se direct quantity add/subtract karke `inventory_movements` table mein adjustment log create kiya jata hai.

---

### Module 5: Live Error & Diagnostic Telemetry Terminal (एरर एवं लॉग्स टर्मिनल)
Database table `app_error_logs` se live exceptions aur tracebacks ko fetch karke browser terminal mein display karta hai:
- Filter by Severity: `INFO`, `WARN`, `ERROR`, `FATAL`.
- Timestamp, HTTP endpoint, error message, aur associated user ID ki instant visibility.

---

## 3. AUTOMATED LAUNCHER SCRIPT (`start_control_panel.bat`)

Developer ya evaluator ke liye 1-click execution script root directory mein provided hai:

```bat
@echo off
echo Starting CycleCare Admin Control Panel...
start http://localhost:5000/admin
node backend/src/server.js
pause
```

Yeh script automated tareeqe se local server initiate karta hai aur default browser mein control panel open kar deta hai.
