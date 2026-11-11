# 09_AUTH_SECURITY_AND_PERMISSIONS.md — Authentication, Authorization, and Security Controls

**Scope:** Complete forensic analysis of authentication mechanisms, cryptographic hashing, JSON Web Tokens, session storage, role-based authorization, administrative keys, and data privacy defenses in CycleCare.  
**Audit Date:** 2026-10-10  
**Evidence Standard:** Middleware modules (`backend/src/middleware/*.js`), controllers (`authController.js`, `adminController.js`), Android security implementations, and Supabase RLS policies.

---

## 1. Authentication Architecture

### 1.1 Credential Storage & Password Hashing
- **Hashing Engine:** `bcryptjs` (Blowfish-based adaptive hashing algorithm).
- **Work Factor (Salt Rounds):** 10 rounds generated via `bcrypt.genSalt(10)`.
- **Implementation Location:** `backend/src/controllers/authController.js` (lines 28, 185).
- **Verification Rule:** `await bcrypt.compare(candidatePassword, storedPasswordHash)` ensures plain-text passwords never match in memory and timing attacks are mitigated.

### 1.2 Access Tokens & JWT Specifications
- **Token Format:** Signed JSON Web Token (RFC 7519).
- **Signing Algorithm:** HMAC using SHA-256 (`HS256`).
- **Secret Key Source:** Loaded via `process.env.JWT_SECRET` with cryptographic fallback.
- **Payload Claims:**
  - `id`: User UUID (Foreign key in relational tables).
  - `email`: User registered email address.
  - `role`: Role string (`USER`, `ADMIN`, `SUPER_ADMIN`).
- **Token Lifetime:** 7 days (`expiresIn: '7d'`).
- **Client Transmission:** Sent via standard HTTP Authorization header: `Authorization: Bearer <jwt_token>`.

### 1.3 Android Mobile Session Persistence
- **Storage Layer:** Android `SharedPreferences` managed through `ApiClient.java`.
- **Biometric Security:** `androidx.biometric:biometric:1.1.0` and `androidx.security:security-crypto:1.1.0-alpha06` are integrated in Gradle dependencies to support hardware fingerprint/biometric locking before revealing sensitive period flow history.
- **Session Expiration Handling:** `AuthInterceptor.java` intercepts `HTTP 401 Unauthorized` responses and triggers navigation back to `LoginActivity.java`.

---

## 2. Authorization & Access Control

### 2.1 Role-Based Access Control (RBAC)
- **Middleware:** `backend/src/middleware/rbac.js` (`authorizeRoles(...roles)`).
- **Supported Hierarchy:**
  - `USER`: Regular mobile consumer; access to own cycle logs, cart, orders, addresses, and circle chats.
  - `ADMIN`: Platform staff; access to product inventory editing, delivery oversight, and customer orders.
  - `SUPER_ADMIN`: Full administrative clearance; access to system KPI stats, user account suspension, and tag reassignment.

### 2.2 Administrative Control Panel Security
- **Authentication Gateway:** Dual-method verification in `backend/src/routes/adminRoutes.js`:
  1. Header Gate: `x-admin-key` header checked against `process.env.ADMIN_SECRET_KEY` (configured default in `adminRoutes.js:10`).
  2. Role Gate: Standard JWT bearer token with `role === 'ADMIN'` or `'SUPER_ADMIN'`.
- **Synthetic Admin Context:** When a valid `x-admin-key` is supplied, the request context is assigned `req.user = { id: '00000000-0000-0000-0000-000000000000', role: 'SUPER_ADMIN' }`. Database writes involving foreign keys explicitly sanitize dummy UUIDs to `NULL` to prevent foreign key constraint violations.

### 2.3 Strict Courier Data Privacy Isolation
- **Security Rule:** Delivery agents operating in "Delivery Agent Mode" must NEVER have visibility into the recipient's reproductive health, cycle phase, flow history, symptoms, or personal notes.
- **Implementation:** `deliveryController.js` and `DeliveryAgentActivity.java` strictly query the `deliveries` and `orders` tables. Delivery responses only transmit `recipient_name`, `delivery_address`, `item_summary`, and `package_count`. Health and cycle APIs reject courier role tokens.

---

## 3. Database-Level Security (PostgreSQL & Supabase RLS)

### 3.1 Row Level Security (RLS) Policies
Defined in `database/migrations/002_rls_policies_and_seed.sql`:
1. `period_logs`: Enabled RLS. Users can only `SELECT`, `INSERT`, `UPDATE`, and `DELETE` rows where `user_id = auth.uid()`.
2. `users` & `profiles`: Users can read their own profile; admins can inspect all profiles.
3. `orders`: Users can only view orders where `user_id = auth.uid()`.
4. `circle_messages`: Senders and recipients can view messages where `sender_id = auth.uid() OR recipient_id = auth.uid()`.

### 3.2 SQL Injection Defenses
All dynamic queries in `backend/src/controllers/adminController.js`, `backend/src/config/supabase.js`, and `backend/src/config/db.js` use parameterized PostgreSQL statements (`$1`, `$2`, `$3` placeholders via `pg.Pool`), eliminating SQL injection vulnerabilities.

---

## 4. API Security & Edge Protection

| Defense Mechanism | Technology | Implementation Location | Operational Behavior |
| :--- | :--- | :--- | :--- |
| **HTTP Security Headers** | `helmet` | `backend/src/app.js:30` | Sets CSP, X-Frame-Options (`SAMEORIGIN`), X-Content-Type-Options (`nosniff`), Strict-Transport-Security. |
| **Rate Limiting** | `express-rate-limit` | `backend/src/app.js:34-39` | Enforces 200 requests per 15-minute window per IP on all `/api/*` endpoints. Returns `HTTP 429` on exceed. |
| **CORS Policy** | `cors` | `backend/src/app.js:31` | Permits cross-origin resource sharing for web dashboard access. |
| **Discreet Packaging** | Database & UI Flag | `orders.is_discreet_packaging` | When true, shipping manifests omit health branding and product descriptions. |

---

## 5. Security Recommendations for Production Deployment

1. **Production Admin Key Rotation:** Replace the development default `ADMIN_SECRET_KEY` in Render environment variables with a 256-bit high-entropy secret.
2. **Production JWT Secret Rotation:** Ensure `JWT_SECRET` in `.env` is distinct from development seeds.
3. **SMS Gateway Integration for Password Resets:** Transition the demo password reset OTP (`1234`) to an authoritative SMS gateway (Twilio, Gupshup, or AWS SNS) when migrating to full production.
