# CYCLECARE — BACKEND SOURCE CODE MAP
## Node.js & Express Architecture, Controllers, Services, Middlewares & Connection Pool

---

## 1. BACKEND FILE DIRECTORY STRUCTURE (डायरेक्टरी संरचना)

CycleCare ka backend Node.js (v18+) aur Express framework par structured **Clean Controller-Service-Repository** pattern follow karta hai:

```
backend/
├── package.json
├── package-lock.json
├── tests/
│   ├── reciprocal_relationship.test.js    <-- 27/27 Tests Passed (100.9s)
│   ├── partner_family_sharing.test.js     <-- 19/19 Tests Passed (95.9s)
│   ├── integration_audit_suite.test.js    <-- 18/18 Tests Passed
│   └── api.test.js                        <-- 12/12 Tests Passed
└── src/
    ├── server.js                          <-- HTTP Server Entry Point & Process Listen
    ├── app.js                             <-- Express App Configuration & Router Mounts
    ├── config/
    │   ├── db.js                          <-- PostgreSQL Pool with DNS Fallback
    │   └── supabase.js                    <-- Supabase Client Initializer
    ├── controllers/
    │   ├── authController.js              <-- Register, Login, Profile
    │   ├── cycleController.js             <-- Period Logs, Predictions, Symptoms
    │   ├── partnerController.js           <-- Reciprocal Tags, Invites, Sharing
    │   ├── chatController.js              <-- Messages, Care Hamper Gifting
    │   ├── ordersController.js            <-- Checkout, Orders, Tracking
    │   ├── deliveryController.js          <-- Courier Dashboard, OTP Verification
    │   ├── productController.js           <-- Product Catalog Management
    │   ├── paymentsController.js          <-- Demo Payment Provider Endpoints
    │   ├── monitoringController.js        <-- DB Pool Stats, Health, Error Telemetry
    │   └── adminController.js             <-- Admin Dashboard Analytics
    ├── routes/
    │   ├── authRoutes.js
    │   ├── cycleRoutes.js
    │   ├── partnerRoutes.js
    │   ├── chatRoutes.js
    │   ├── ordersRoutes.js
    │   ├── deliveryRoutes.js
    │   ├── productRoutes.js
    │   ├── paymentsRoutes.js
    │   ├── monitoringRoutes.js
    │   └── adminRoutes.js
    ├── services/
    │   ├── relationshipMappingService.js  <-- Bi-directional Reciprocal Tag Mapping Logic
    │   ├── paymentProvider.js             <-- Pluggable Abstract & Demo Payment Provider
    │   └── notificationService.js         <-- Push Notifications & Alerts Dispatcher
    ├── middlewares/
    │   ├── authMiddleware.js              <-- JWT Verification (`authenticateToken`)
    │   ├── adminMiddleware.js             <-- Admin Role Authorization Guard
    │   └── errorHandler.js                <-- Global Error Catcher & JSON Responder
    └── views/
        └── admin.html                     <-- Single-Page Admin Web Dashboard
```

---

## 2. CORE ENTRY POINTS & CONFIGURATION (सर्वर और कॉन्फ़िगरेशन)

### 2.1 Server Bootstrap (`backend/src/server.js`)
- **Port Selection:** Checks `process.env.PORT` or defaults to `5000`.
- **Initialization:** Starts the HTTP server instance and prints verified startup banners.
- **Graceful Shutdown:** Listens for `SIGTERM` and `SIGINT` signals, closes active HTTP sockets, and releases database pool clients cleanly to prevent hung connections in Supabase PgBouncer.

### 2.2 Express Application Setup (`backend/src/app.js`)
- **Security Headers:** Configures `helmet()` for content security and HTTP hardening.
- **CORS Handling:** Allows cross-origin requests from web admin (`http://localhost:5000` / production domain) and Android user-agents.
- **Request Parsing:** Mounts `express.json({ limit: '10mb' })` and `express.urlencoded({ extended: true })`.
- **Request Logging:** Uses `morgan('dev')` in non-test environments for HTTP traffic monitoring.
- **Static Assets:** Serves `admin.html` on `GET /admin` and health check on `GET /api/v1/health`.
- **Router Mounting:** Mounts all 10 domain routes under `/api/v1/*`.

### 2.3 PostgreSQL Pool with Dual DNS Fallback (`backend/src/config/db.js`)
- **Forensic Problem:** Supabase pooler host (`aws-0-ap-southeast-2.pooler.supabase.com`) resolves over IPv4/IPv6. On many ISP connections or Render environments, default DNS servers fail with `ENOTFOUND` or `ETIMEDOUT`.
- **Implementation:**
  ```javascript
  const dns = require('dns');
  // Explicitly configure globally trusted DNS servers
  dns.setServers(['8.8.8.8', '1.1.1.1', '8.8.4.4']);

  const { Pool } = require('pg');
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000
  });
  ```

---

## 3. BUSINESS CONTROLLERS BREAKDOWN (कंट्रोलर्स का विस्तृत विवरण)

### 3.1 `partnerController.js` (पार्टनर एवं रेसिप्रोकल टैगिंग)
- **Key Methods:**
  - `assignRelationshipTag(req, res)`: User ke selected tag aur user ke profile gender ko inspect karta hai. `relationshipMappingService` call karke automatic reciprocal relationship calculate karta hai. Ek hi SQL transaction mein both perspectives update karta hai aur `sharing_audit_events` mein entry create karta hai.
  - `getPartnerDashboard(req, res)`: Current user ke verified partner connection, reciprocal tag, cycle status, aur permission filter apply karke sanitized data return karta hai.
  - `updatePermissions(req, res)`: User dwara set ki gayi granular sharing permissions (`share_phase`, `share_symptoms`, `share_predictions`, `share_mood`) ko update karta hai.

### 3.2 `deliveryController.js` (डिलीवरी एजेंट मोड एवं कूरियर प्राइवेसी)
- **Key Methods:**
  - `getAgentDashboard(req, res)`: Active pending deliveries fetch karta hai. **Strict Privacy Filter:** Query select clause mein user ki health ya period columns strictly excluded hote hain. Courier ko sirf name, address, package description, aur contact milta hai.
  - `startDelivery(req, res)`: Delivery status ko `OUT_FOR_DELIVERY` mark karta hai aur initial route coordinate inject karta hai.
  - `simulateMovement(req, res)`: Courier progress ko step-by-step simulate karta hai (25%, 50%, 75%, 90%, 100%) aur ETA update karta hai.
  - `completeDelivery(req, res)`: User ke secret OTP (`4821`) ko verify karta hai. Match hone par hi order ko `DELIVERED` mark karta hai.

### 3.3 `ordersController.js` (ऑर्डर मैनेजमेंट एवं चेकआउट)
- **Key Methods:**
  - `createOrder(req, res)`: Cart items, shipping address, aur payment mode process karta hai. Database transaction mein `orders`, `order_items`, aur corresponding `deliveries` row simultaneously create karta hai.
  - `getOrderTracking(req, res)`: Order state, delivery agent current location, timeline events, aur recipient ke liye secret `delivery_otp` return karta hai.

### 3.4 `cycleController.js` (साइकल वेलनेस एवं एआई प्रिडिक्शंस)
- **Key Methods:**
  - `logPeriod(req, res)`: Start date, end date, flow intensity, cramp rating (1-5), aur notes insert karta hai.
  - `getPredictions(req, res)`: User ke historical period logs ka weighted moving average calculate karta hai. Menstrual phase, follicular phase, ovulation peak (Day 14), aur luteal phase dates forecast karta hai.

---

## 4. DOMAIN SERVICES ARCHITECTURE (डोमेन सर्विसेज)

### 4.1 `relationshipMappingService.js` (रेसिप्रोकल मैपिंग लॉजिक)
Yeh service complex family aur partner relationship matrix ko calculate karti hai:

```javascript
class RelationshipMappingService {
  static getReciprocalTag(assignedTag, userGender) {
    const normalizedTag = (assignedTag || '').trim().toLowerCase();
    const gender = (userGender || '').trim().toLowerCase();

    // 1. Spousal / Romantic Pairs
    if (normalizedTag === 'husband') return 'Wife';
    if (normalizedTag === 'wife') return 'Husband';
    if (normalizedTag === 'boyfriend') return 'Girlfriend';
    if (normalizedTag === 'girlfriend') return 'Boyfriend';

    // 2. Parent-Child Reciprocal Relationships
    if (normalizedTag === 'father' || normalizedTag === 'mother') {
      return gender === 'male' ? 'Son' : 'Daughter';
    }
    if (normalizedTag === 'daughter' || normalizedTag === 'son') {
      return gender === 'male' ? 'Father' : 'Mother';
    }

    // 3. Sibling Reciprocal Relationships
    if (normalizedTag === 'brother' || normalizedTag === 'sister') {
      return gender === 'male' ? 'Brother' : 'Sister';
    }

    // 4. Default Fallback
    return 'Partner';
  }
}
```

### 4.2 `paymentProvider.js` (प्लग-एंड-प्ले पेमेंट प्रोवाइडर)
- **Abstract Interface:** `PaymentProvider` class (`createPayment`, `processPayment`, `refundPayment`).
- **Concrete Provider:** `DemoPaymentProvider` class jo realistic latency simulate karta hai, transaction IDs generate karta hai, aur instant payment confirmation provide karta hai.

---

## 5. MIDDLEWARES & ERROR PIPELINE (मिडिलवेयर्स और सुरक्षा गार्ड्स)

### 5.1 `authMiddleware.js` (`authenticateToken`)
- Request ke `Authorization` header se Bearer token extract karta hai.
- `jwt.verify(token, process.env.JWT_SECRET)` se token validate karta hai.
- Valid hone par `req.user = decoded` attach karta hai; invalid hone par `401 Unauthorized` ya `403 Forbidden` return karta hai.

### 5.2 `errorHandler.js` (ग्लोबल एरर हैंडलर)
- Sabhi unhandled synchronous aur asynchronous exceptions ko catch karta hai.
- Error message, stack trace, aur origin ko `app_error_logs` database table mein record karta hai.
- Client ko sanitized JSON error response send karta hai bina sensitive database credentials expose kiye.
