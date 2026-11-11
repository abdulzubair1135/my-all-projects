# CycleCare Security & Privacy Architecture

## 1. Core Principles
- **Privacy-First Data Protection:** Menstrual cycle data and symptom logs belong exclusively to the user.
- **Zero Secret Leakage:** APK binaries and GitHub repositories strictly contain zero production API keys, service role keys, DB passwords, or gateway secrets.
- **Server-Side Verification:** Price calculation, discount application, stock deduction, and payment confirmations are enforced strictly by the Node.js backend.
- **Minimal Access:** Admins have audit logs and catalog access but no unauthorized exposure to raw personal cycle logs.

## 2. Authentication & Authorization
- Passwords are hashed using bcrypt prior to database storage.
- JWT tokens (short-lived access token + securely stored refresh token) handle REST authorization.
- Role-Based Access Control (RBAC) enforces `USER`, `ADMIN`, and `SUPER_ADMIN` boundaries on express endpoints.
- Row Level Security (RLS) on Supabase PostgreSQL ensures data separation at the database layer.

## 3. Client-Side Security (Android)
- **App Lock:** Local PIN code and BiometricPrompt API (Fingerprint / Face Unlock).
- **Discreet Notifications:** Option for obfuscated notification payload titles (e.g. "CycleCare: You have a reminder") to protect user privacy in public settings.
- **Data Export & Erasure:** In-app triggers to download offline JSON exports or permanently delete user cycle data / accounts.
- **AI Permission Gate:** Data sharing with the "Ask CycleCare" AI assistant is strictly opt-in per prompt.

## 4. Payment Gateway Security
- Razorpay order creation originates server-side (`POST /payments/create`).
- Order confirmation (`POST /payments/verify`) validates HMAC-SHA256 signatures server-side against the `RAZORPAY_KEY_SECRET`.
- Webhooks (`POST /payments/webhook`) process asynchronous payments securely.
