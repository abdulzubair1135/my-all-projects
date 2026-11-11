# 03_SYSTEM_ARCHITECTURE.md — System Architecture & Component Design

**Scope:** Architectural blueprint of CycleCare covering client-server topology, component interactions, database models, authentication workflows, and deployment infrastructure.  
**Audit Date:** 2026-10-10  
**Verification Method:** Static call graph analysis, Android Manifest inspection, Express router mapping, and live database query tracing.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph MobileClient["Android Native Mobile Application (Java 8)"]
        UI["Activities, Fragments & XML Views"]
        VM["ViewModels & Repositories"]
        Room["Local Room SQLite DB (period_logs, sync_queue)"]
        Worker["WorkManager (SyncWorker)"]
        NetClient["Retrofit 2 & OkHttp (ApiClient)"]
    end

    subgraph CloudEdge["Edge Network & Cloud Infrastructure"]
        CF["Cloudflare Edge CDN"]
        Render["Render Web Service (Linux Container)"]
    end

    subgraph BackendAPI["CycleCare Node.js REST API Server"]
        Express["Express 4 Application (app.js)"]
        Security["Helmet & RateLimiter & CORS"]
        AuthMiddleware["JWT & RBAC Middleware"]
        Controllers["17 Express Controllers"]
        SQLAdapter["Dynamic PostgreSQL Adapter (supabase.js)"]
        Pool["pg.Pool Connection Pool (db.js)"]
        AdminView["Admin Single-Page Web Dashboard (admin.html)"]
    end

    subgraph DataTier["Data Tier & External Integrations"]
        PG["Supabase PostgreSQL 15.6 (52 Tables)"]
        FCM["Firebase Cloud Messaging (FCM Push)"]
        Razorpay["Razorpay Payment Gateway"]
        GoogleMaps["Google Maps & Fused Location API"]
    end

    UI --> VM
    VM --> Room
    VM --> NetClient
    Room --> Worker
    Worker --> NetClient
    NetClient -->|HTTPS /api/v1/| CF
    AdminView -->|HTTPS /api/v1/admin/| Express
    CF --> Render
    Render --> Express
    Express --> Security
    Security --> AuthMiddleware
    AuthMiddleware --> Controllers
    Controllers --> SQLAdapter
    SQLAdapter --> Pool
    Pool -->|Port 6543 SSL| PG
    Controllers --> FCM
    Controllers --> Razorpay
    UI --> GoogleMaps
```

---

## 2. Android Client Component Architecture (MVVM)

```mermaid
flowchart LR
    subgraph ViewLayer["View Layer (UI)"]
        Act["Activities (MainActivity, PeriodLog, CircleChat)"]
        Frag["Fragments (HomeFragment, CalendarFragment, StoreFragment)"]
        Views["Custom Views & Panda Mascot Animators"]
    end

    subgraph DomainLayer["Domain / Repository Layer"]
        Repo["CycleRepository / StoreRepository"]
        Sched["CycleNotificationScheduler"]
    end

    subgraph LocalData["Local Persistence (Room)"]
        AppDB["AppDatabase (SQLite)"]
        PeriodDAO["PeriodLogDao"]
        SyncDAO["SyncQueueDao"]
    end

    subgraph NetworkData["Network Layer"]
        Retro["ApiService (Retrofit 2)"]
        AuthInt["AuthInterceptor (Bearer JWT)"]
        Sync["SyncWorker (WorkManager)"]
    end

    Act --> Repo
    Frag --> Repo
    Repo --> PeriodDAO
    Repo --> SyncDAO
    PeriodDAO --> AppDB
    SyncDAO --> AppDB
    Repo --> Retro
    Sync --> SyncDAO
    Sync --> Retro
    Retro --> AuthInt
```

---

## 3. Backend Module & Router Architecture

The backend implements a modular, decoupled Express REST design:

```
src/
├── app.js                          # Core Express initialization & route registry
├── server.js                       # HTTP listener binding on process.env.PORT
├── config/
│   ├── db.js                       # Authoritative pg.Pool direct connection
│   ├── supabase.js                 # Query adapter providing .from().select() syntax
│   └── razorpay.js                 # Razorpay client instance
├── middleware/
│   ├── auth.js                     # authenticateToken JWT verification
│   ├── rbac.js                     # authorizeRoles('USER', 'ADMIN', 'SUPER_ADMIN')
│   └── errorHandler.js             # Formats errors into { success: false, message, code }
├── controllers/                    # 17 Feature Controllers
│   ├── authController.js           # Signup, Login, Demo Auth, Password Reset
│   ├── cycleController.js          # Period Logging, Cycles, Predictions
│   ├── chatController.js           # Trusted Circle WhatsApp-style Messaging & Tags
│   ├── deliveryController.js       # Courier Dispatch, Simulation, OTP Handoff
│   ├── adminController.js          # Raw SQL Analytics, User Tags, Chat Monitoring
│   ├── ordersController.js         # Checkout, Order Lifecycle, Recipient Tracking
│   ├── paymentsController.js       # Razorpay & DemoPaymentProvider
│   └── ... (10 additional controllers)
├── routes/                         # 17 Express Router Modules (mounted at /api/v1/*)
├── services/
│   ├── cycleService.js             # Ovulation and Phase Prediction Calculation
│   ├── notificationService.js      # Firebase Cloud Messaging Delivery
│   ├── paymentProvider.js          # Abstract & Concrete Demo Payment Engine
│   └── paymentService.js           # Razorpay Signature Verification
└── views/
    └── admin.html                  # Single-Page Admin Web Panel
```

---

## 4. Database Relationship Topology (Core Entities)

```mermaid
erDiagram
    users ||--o| profiles : "has profile"
    users ||--o| cycle_settings : "configures"
    users ||--o{ period_logs : "records"
    users ||--o{ symptom_logs : "logs"
    users ||--o{ mood_logs : "logs"
    users ||--o{ addresses : "saves"
    users ||--o{ orders : "places"
    orders ||--|{ order_items : "contains"
    products ||--o{ order_items : "referenced in"
    products ||--o{ inventory_movements : "tracked by"
    users ||--o{ partner_connections : "shares cycle with"
    users ||--o{ circle_messages : "sends"
    users ||--o{ user_follows : "follows"
    orders ||--o| deliveries : "dispatched via"
    deliveries ||--o{ delivery_events : "generates"
    deliveries ||--o| delivery_live_locations : "telemetry"
```

---

## 5. End-to-End Authentication Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Mobile User / Admin
    participant Mobile as Android / Admin Web
    participant Server as Node.js Backend (/api/v1/auth)
    participant DB as Supabase PostgreSQL

    User->>Mobile: Enters Email & Password
    Mobile->>Server: POST /api/v1/auth/login
    Server->>DB: SELECT id, password_hash, role, status FROM users WHERE email = $1
    DB-->>Server: Return User Record
    Server->>Server: bcrypt.compare(password, password_hash)
    alt Password Valid
        Server->>Server: jwt.sign({ id, email, role }, JWT_SECRET, { expiresIn: '7d' })
        Server-->>Mobile: HTTP 200 { success: true, token, user }
        Mobile->>Mobile: Persist Token in EncryptedSharedPreferences / localStorage
    else Password Invalid
        Server-->>Mobile: HTTP 401 { success: false, message: "Invalid credentials" }
    end
```

---

## 6. End-to-End Delivery & 4-Digit OTP Handoff Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Customer as CycleCare Customer
    participant AndroidCustomer as Customer App (OrderTrackingActivity)
    participant Backend as Express Backend
    participant DB as PostgreSQL
    participant CourierApp as Courier App (DeliveryAgentActivity)
    actor Courier as Delivery Courier

    Customer->>Backend: Complete Checkout (#CC-DEMO-1001)
    Backend->>DB: INSERT INTO orders & deliveries (delivery_otp = '4821')
    Backend-->>AndroidCustomer: Displays "Delivery OTP: 4821" (Confidential to Recipient)
    
    Courier->>CourierApp: Opens Delivery Agent Dashboard
    CourierApp->>Backend: POST /api/v1/deliveries/:id/accept
    CourierApp->>Backend: POST /api/v1/deliveries/:id/start
    CourierApp->>Backend: POST /api/v1/deliveries/:id/simulate (Step 25% -> 50% -> 90%)
    Backend->>AndroidCustomer: Live Map updates courier marker & ETA (~15 mins)
    
    CourierApp->>Backend: POST /api/v1/deliveries/:id/arrived
    Courier->>Customer: Courier arrives at doorstep, asks for OTP
    Customer->>Courier: Recipient shares verbal OTP "4821"
    Courier->>CourierApp: Inputs "4821" in Complete Delivery Dialog
    CourierApp->>Backend: POST /api/v1/deliveries/:id/complete { delivery_otp: "4821" }
    Backend->>DB: Verify delivery_otp == '4821'; Update order & delivery status to DELIVERED
    Backend-->>CourierApp: HTTP 200 { success: true, message: "Delivered successfully" }
    Backend-->>AndroidCustomer: Order marked DELIVERED; Timeline completed
```

---

## 7. Offline-First Cycle Data Synchronization Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Cycle Tracker
    participant UI as PeriodLogActivity
    participant Room as Room SQLite (period_logs, sync_queue)
    participant Worker as SyncWorker (WorkManager)
    participant API as REST API (/api/v1/cycle/log)
    participant DB as Supabase PostgreSQL

    User->>UI: Logs Period Flow, Pain Level, Moods (Offline/No Internet)
    UI->>Room: INSERT INTO period_logs (status: "PENDING_SYNC")
    UI->>Room: INSERT INTO sync_queue (action: "LOG_PERIOD", payload: JSON)
    UI-->>User: Instant UI Feedback ("Saved locally")
    
    Note over Worker: Network connectivity restored
    Worker->>Room: SELECT * FROM sync_queue ORDER BY created_at ASC
    Worker->>API: POST /api/v1/cycle/log (Batch Payload)
    API->>DB: INSERT INTO period_logs (flow, start_date, symptoms)
    DB-->>API: Success Response
    API-->>Worker: HTTP 201 Created
    Worker->>Room: UPDATE period_logs SET status = 'SYNCED'
    Worker->>Room: DELETE FROM sync_queue WHERE id = queue_id
```
