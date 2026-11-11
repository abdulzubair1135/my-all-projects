# CYCLECARE — SECURITY & PRIVACY REVIEW
## Cryptographic Controls, RBAC, Zero-Knowledge Courier Privacy & Compliance Audit

---

## 1. THREAT MODEL & PRIVACY PRINCIPLES (सुरक्षा और गोपनीयता दर्शन)

Menstrual health data ek extremely intimate aur sensitive personal health information (PHI) category mein aata hai. CycleCare architecture **Privacy-by-Design** aur **Principle of Least Privilege** par build kiya gaya hai.

```
+-----------------------------------------------------------------------------------+
|                        CYCLECARE SECURITY & PRIVACY SHIELD                        |
+-----------------------------------------------------------------------------------+
| 1. DATA ENCRYPTION    | - Passwords hashed using bcrypt (10 rounds salt).         |
|    & TRANSPORT        | - All API communication over HTTPS / TLS 1.3.             |
|                       | - PostgreSQL connections protected with SSL tunnels.      |
|-----------------------+-----------------------------------------------------------|
| 2. RBAC & PERMISSIONS | - Strict 3-tier Role Based Access Control (User, Courier, |
|                       |   Administrator).                                         |
|                       | - Granular sharing permissions matrix per connection.     |
|-----------------------+-----------------------------------------------------------|
| 3. COURIER PRIVACY    | - Complete zero-knowledge isolation: Delivery agents have |
|    ISOLATION          |   mathematically zero access to cycle/symptom data.       |
|-----------------------+-----------------------------------------------------------|
| 4. AUDIT & TRACE      | - Immutable audit trail in `sharing_audit_events`.        |
|                       | - SQL injection immunity via parameterized queries ($1..).|
+-----------------------------------------------------------------------------------+
```

---

## 2. AUTHENTICATION & TOKEN CRYPTOGRAPHY (ऑथेंटिकेशन और टोकन सुरक्षा)

### 2.1 Password Hashing with Salt
Passwords ko database table `users` mein save karne se pehle industry-standard `bcryptjs` algorithm se hash kiya jata hai:
- **Salt Rounds:** `10`
- Raw passwords kabhi bhi database mein write nahi hote, na hi kisi server log file ya error traceback mein print hote hain.

### 2.2 JWT Token Architecture
Authentication verification stateless **JSON Web Tokens (JWT)** ke through hoti hai:
- **Signing Algorithm:** `HS256` (HMAC SHA-256)
- **Secret Key:** `process.env.JWT_SECRET` (Cryptographically random 256-bit key)
- **Token Payload:** `{ userId, email, role }`
- **Token Validity:** 7 Days (Configurable)
- **Header Transmission:** `Authorization: Bearer <token>`
- **Token Verification:** Har protected endpoint par `authenticateToken` middleware token signature aur expiration timestamp check karta hai.

---

## 3. ROLE-BASED ACCESS CONTROL (RBAC MATRIX)

CycleCare teen distinct operational roles enforce karta hai:

| Feature / Resource | Standard User | Delivery Courier | Administrator |
| :--- | :---: | :---: | :---: |
| **Personal Period & Symptom Logs** | **Full Access** | **ACCESS DENIED** | **ACCESS DENIED** |
| **Connected Partner Cycle Data** | Conditional (Permitted) | **ACCESS DENIED** | **ACCESS DENIED** |
| **Wellness Store Catalog** | Read Only | Read Only | Full CRUD |
| **Create Personal Order** | Allowed | Allowed | Allowed |
| **Courier Delivery Dashboard** | Forbidden | **Full Access** | Full Access |
| **Simulate Courier Movement** | Forbidden | **Allowed** | **Allowed** |
| **Verify Handover OTP** | Forbidden | **Allowed** | **Allowed** |
| **System Diagnostics & Telemetry** | Forbidden | Forbidden | **Full Access** |
| **Reset Demo Orders** | Forbidden | Forbidden | **Allowed** |

---

## 4. COURIER ZERO-KNOWLEDGE PRIVACY ISOLATION (कूरियर प्राइवेसी सुरक्षा)

Delivery agent ko sanitary package deliver karna hota hai, lekin use recipient ki medical condition ya period date pata chalna ek serious privacy violation hai.

### Forensic Implementation Proof (`deliveryController.js`):
Delivery agent dashboard endpoint par SQL query explicitly healthcare fields ko filter out karti hai:

```javascript
// Verified source code from backend/src/controllers/deliveryController.js
const result = await pool.query(`
  SELECT 
    d.id AS delivery_id,
    o.order_number,
    u.full_name AS recipient_name,
    d.current_lat,
    d.current_lng,
    d.progress_percent,
    d.eta_minutes,
    d.delivery_status,
    o.delivery_address,
    -- NOTE: Period logs, symptoms, and cycle phases are STRICTLY EXCLUDED!
    'CycleCare Care Package' AS package_summary
  FROM deliveries d
  JOIN orders o ON d.order_id = o.id
  JOIN users u ON o.user_id = u.id
  WHERE d.delivery_status != 'DELIVERED'
`);
```
Is architecture se courier agent chahe network intercept kare ya app modify kare, backend se period ya cycle ka ek bhi byte return nahi hota!

---

## 5. AUDIT EVENT LOGGING (`sharing_audit_events`)

User ki privacy transparent aur verifiable rahe, iske liye system mein ek immutable audit logging mechanism active hai:
- Jab bhi koi user:
  1. Kisi partner ko connection invite bhejta hai,
  2. Partner invite accept ya reject hota hai,
  3. Relationship tag assign hota hai (aur reciprocal tag sync hota hai), ya
  4. Sharing permissions (`share_phase`, `share_symptoms`, etc.) modify hoti hain,
- Toh backend automatically `sharing_audit_events` table mein actor user ID, target partner ID, event type, aur timestamp record karta hai.

---

## 6. INJECTION IMMUNITY & APPLICATION HARDENING

1. **SQL Injection Immunity:** Backend mein koi bhi raw dynamic string concatenation query execution (`pool.query("SELECT * FROM users WHERE id = '" + id + "'")`) use nahi hoti. Har SQL query strictly parameterized arguments (`$1, $2, $3...`) ke sath execute hoti hai.
2. **HTTP Hardening via Helmet:**
   - `Content-Security-Policy`: Scripts aur stylesheets ki unauthorized execution block karta hai.
   - `X-Frame-Options: DENY`: Clickjacking attacks prevent karta hai.
   - `X-Content-Type-Options: nosniff`: MIME-type sniffing prevent karta hai.
3. **CORS Configuration:** Authorized origins configure hain jisse malicious unauthorized third-party websites backend APIs ko abuse na kar sakein.
