# CYCLECARE — COMPLETE API REFERENCE
## Comprehensive RESTful API Specification, Payloads, Codes & Security Standards

---

## 1. GLOBAL API STANDARDS & CONVENTIONS (सामान्य नियम और प्रोटोकॉल)

CycleCare backend REST APIs industrial best practices ke according standardize kiye gaye hain:

- **Base URL (Local Daemon):** `http://localhost:5000/api/v1`
- **Base URL (Cloud Deployment):** `https://cyclecare-backend.onrender.com/api/v1`
- **Content-Type:** `application/json; charset=utf-8`
- **Authentication Scheme:** HTTP Bearer Authentication Token
  ```http
  Authorization: Bearer <jwt_access_token>
  ```
- **Standard Success Format:**
  ```json
  {
    "success": true,
    "data": { ... },
    "message": "Operation completed successfully"
  }
  ```
- **Standard Error Format:**
  ```json
  {
    "success": false,
    "error": "Descriptive error message",
    "code": "ERROR_CONSTANT_NAME"
  }
  ```

---

## 2. API ENDPOINT REGISTRY SUMMARY (समस्त एपीआई सूची)

| Domain | Route Prefix | Endpoints Count | Key Responsibility |
| :--- | :--- | :--- | :--- |
| **System & Health** | `/api/v1/health` | 1 | Basic liveness probe |
| **Authentication & Profile** | `/api/v1/auth` | 5 | User signup, login, profile edit, FCM tokens |
| **Cycle Wellness & Logging** | `/api/v1/cycle` | 5 | Period logs, symptom tracker, cycle phase AI predictions |
| **Partner Care & Sharing** | `/api/v1/partner` | 7 | Invites, connections, reciprocal tags, privacy permissions |
| **Circle Care Chat** | `/api/v1/chat` | 4 | Real-time messages, care pack gifting cards |
| **Wellness E-Commerce Store** | `/api/v1/products` | 3 | Product catalog browsing, details, admin catalog update |
| **Orders & Checkout** | `/api/v1/orders` | 5 | Order placement, history, tracking, cancelation |
| **Express Deliveries** | `/api/v1/deliveries` | 9 | Courier dashboard, live dispatch steps, OTP verification |
| **Payments Integration** | `/api/v1/payments` | 4 | Demo payment lifecycle (Create, Success, Fail, Cancel) |
| **System Telemetry & Health** | `/api/v1/monitoring`| 5 | DB latency, pooler health, memory counters, error logs |
| **Admin Control Panel** | `/api/v1/admin` | 4 | Business metrics, system stats, inventory adjust |
| **Total Active Endpoints** | — | **52 Endpoints**| Fully operational full-stack system |

---

## 3. DOMAIN-BY-DOMAIN DETAILED ENDPOINT SPECIFICATION

### Domain 1: Authentication & User Profile (`/api/v1/auth`)

#### 1.1 Register New User
- **Method / Path:** `POST /api/v1/auth/register`
- **Authentication:** None (Public)
- **Request Body:**
  ```json
  {
    "email": "aastha@cyclecare.app",
    "password": "SecurePassword123!",
    "fullName": "Aastha Sharma",
    "gender": "female",
    "inviteCode": "PARTNER-1024" // Optional
  }
  ```
- **Response `201 Created`:**
  ```json
  {
    "success": true,
    "message": "User registered successfully",
    "token": "eyJhbGciOiJIUzI1NiIsIn...",
    "user": {
      "id": "c1f7a012-3456-7890-abcd-ef0123456789",
      "email": "aastha@cyclecare.app",
      "fullName": "Aastha Sharma",
      "role": "user"
    }
  }
  ```

#### 1.2 User Login
- **Method / Path:** `POST /api/v1/auth/login`
- **Authentication:** None (Public)
- **Request Body:**
  ```json
  {
    "email": "delivery.demo@cyclecare.app",
    "password": "CycleCareDemo123!"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "e4444444-4444-4444-4444-444444444444",
      "email": "delivery.demo@cyclecare.app",
      "fullName": "CycleCare Delivery Courier",
      "role": "delivery_agent"
    }
  }
  ```

#### 1.3 Update User Profile
- **Method / Path:** `PUT /api/v1/auth/profile`
- **Authentication:** Required (`Bearer <token>`)
- **Request Body:**
  ```json
  {
    "cycleLength": 28,
    "periodDuration": 5,
    "lastPeriodDate": "2026-10-01",
    "themePreference": "dark"
  }
  ```
- **Response `200 OK`:** Profile updated successfully.

---

### Domain 2: Cycle Tracking & Predictions (`/api/v1/cycle`)

#### 2.1 Log Period & Flow
- **Method / Path:** `POST /api/v1/cycle/logs`
- **Authentication:** Required (`Bearer <token>`)
- **Request Body:**
  ```json
  {
    "startDate": "2026-10-01",
    "endDate": "2026-10-05",
    "flowIntensity": "medium",
    "crampLevel": 3,
    "mood": "calm",
    "notes": "Mild fatigue in the afternoon"
  }
  ```
- **Response `201 Created`:** Period record created with auto-calculated duration.

#### 2.2 Get Phase Predictions & Insights
- **Method / Path:** `GET /api/v1/cycle/predictions`
- **Authentication:** Required (`Bearer <token>`)
- **Response `200 OK`:**
  ```json
  {
    "currentCycleDay": 11,
    "currentPhase": "follicular",
    "phaseDescription": "Energy rising, preparing for ovulation window",
    "nextPeriodDate": "2026-10-29",
    "ovulationWindow": {
      "start": "2026-10-12",
      "peak": "2026-10-14",
      "end": "2026-10-16"
    },
    "fertilityStatus": "high"
  }
  ```

---

### Domain 3: Partner Care & Reciprocal Sharing (`/api/v1/partner`)

#### 3.1 Assign Relationship & Auto Reciprocal Sync
- **Method / Path:** `POST /api/v1/partner/tags`
- **Authentication:** Required (`Bearer <token>`)
- **Request Body:**
  ```json
  {
    "partnerId": "b2222222-2222-2222-2222-222222222222",
    "relationshipTag": "Husband"
  }
  ```
- **Business Logic:**
  Backend checks requester's gender (female). Determines reciprocal tag (`Wife`).
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "message": "Relationship tagged successfully with reciprocal synchronization",
    "relationshipTag": "Husband",
    "reciprocalTag": "Wife"
  }
  ```

#### 3.2 Update Granular Sharing Permissions
- **Method / Path:** `PUT /api/v1/partner/permissions`
- **Authentication:** Required (`Bearer <token>`)
- **Request Body:**
  ```json
  {
    "partnerId": "b2222222-2222-2222-2222-222222222222",
    "sharePhase": true,
    "shareSymptoms": false,
    "sharePredictions": true,
    "shareMood": true
  }
  ```
- **Response `200 OK`:** Permissions updated and logged to `sharing_audit_events`.

---

### Domain 4: Circle Care Chat & Gifting (`/api/v1/chat`)

#### 4.1 Send Chat Message
- **Method / Path:** `POST /api/v1/chat/send`
- **Authentication:** Required (`Bearer <token>`)
- **Request Body:**
  ```json
  {
    "recipientId": "b2222222-2222-2222-2222-222222222222",
    "content": "Hey! How are you feeling today?",
    "messageType": "text"
  }
  ```

#### 4.2 Send Care Item Hamper in Chat
- **Method / Path:** `POST /api/v1/chat/care-item`
- **Authentication:** Required (`Bearer <token>`)
- **Request Body:**
  ```json
  {
    "recipientId": "a1111111-1111-1111-1111-111111111111",
    "productId": "p001-cramp-relief-patch",
    "customNote": "Hope this helps with the cramps!"
  }
  ```
- **Response `201 Created`:** Message saved as `type: 'CARE_ITEM'` containing product card payload.

---

### Domain 5: Wellness Store, Orders & Courier Dispatch (`/api/v1/orders` & `/deliveries`)

#### 5.1 Place Order
- **Method / Path:** `POST /api/v1/orders`
- **Authentication:** Required (`Bearer <token>`)
- **Request Body:**
  ```json
  {
    "items": [
      { "productId": "p-01", "quantity": 2, "price": 299 }
    ],
    "deliveryAddress": "Flat 402, Lotus Orchid, Pune",
    "paymentMethod": "DEMO"
  }
  ```
- **Response `201 Created`:**
  ```json
  {
    "orderId": "cc-demo-1001",
    "orderNumber": "#CC-DEMO-1001",
    "status": "PAID",
    "deliveryOtp": "4821",
    "estimatedDelivery": "15-25 minutes"
  }
  ```

#### 5.2 Delivery Agent Dashboard
- **Method / Path:** `GET /api/v1/deliveries/agent/dashboard`
- **Authentication:** Required (`Bearer <token>`)
- **Response `200 OK` (Courier Isolation Verified!):**
  ```json
  {
    "activeCount": 1,
    "deliveries": [
      {
        "deliveryId": "del-101",
        "orderNumber": "#CC-DEMO-1001",
        "recipientName": "Aastha Sharma",
        "address": "Flat 402, Lotus Orchid, Pune",
        "packageType": "CycleCare Wellness Pack (2 items)",
        "status": "OUT_FOR_DELIVERY",
        "menstrualPhase": null, // STRICTLY NULL!
        "symptoms": null        // STRICTLY NULL!
      }
    ]
  }
  ```

#### 5.3 Complete Delivery with OTP Handover
- **Method / Path:** `POST /api/v1/deliveries/:id/complete`
- **Authentication:** Required (`Bearer <token>`)
- **Request Body:**
  ```json
  {
    "otp": "4821"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "message": "Delivery verified and marked as DELIVERED",
    "deliveredAt": "2026-10-11T01:30:00Z"
  }
  ```

---

### Domain 6: System Monitoring & Admin Control (`/api/v1/monitoring` & `/admin`)

#### 6.1 Database Connection Pool Status
- **Method / Path:** `GET /api/v1/monitoring/pool-status`
- **Authentication:** Admin Token / Internal
- **Response `200 OK`:**
  ```json
  {
    "database": "Supabase PostgreSQL Pooler",
    "host": "aws-0-ap-southeast-2.pooler.supabase.com",
    "poolStats": {
      "totalClients": 5,
      "idleClients": 4,
      "waitingClients": 0
    },
    "pingLatencyMs": 42.6,
    "dnsFallbackActive": true,
    "dnsServers": ["8.8.8.8", "1.1.1.1"]
  }
  ```

#### 6.2 Admin Live System Statistics
- **Method / Path:** `GET /api/v1/admin/stats`
- **Authentication:** Admin Token
- **Response `200 OK`:**
  ```json
  {
    "totalUsers": 1284,
    "totalPeriodLogs": 4920,
    "totalOrders": 312,
    "activeDeliveries": 4,
    "lowStockProducts": 2,
    "systemHealth": "OPTIMAL"
  }
  ```
