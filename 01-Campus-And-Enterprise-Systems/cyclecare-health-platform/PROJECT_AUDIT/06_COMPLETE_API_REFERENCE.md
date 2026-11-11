# 06_COMPLETE_API_REFERENCE.md — Complete API and Endpoint Reference

**Scope:** Exhaustive catalog of all 68 REST API endpoints exposed by the CycleCare Node.js Express server.  
**Audit Date:** 2026-10-10  
**Base URL:**
- Production / Live: `https://cyclecare-57my.onrender.com/api/v1/`
- Local Development: `http://localhost:5000/api/v1/`
**Evidence Standard:** Route files (`backend/src/routes/*.js`), controller functions (`backend/src/controllers/*.js`), and Retrofit interface (`android/app/src/main/java/com/cyclecare/api/ApiService.java`).

---

## 1. Authentication Endpoints (`/api/v1/auth`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `POST` | `/auth/register` | New user signup with gender selection | None | `{ email, password, display_name, gender }` | `{ success, user, token }` | `VERIFIED` |
| `POST` | `/auth/login` | Email/password login | None | `{ email, password }` | `{ success, user, token }` | `VERIFIED` |
| `POST` | `/auth/demo-login` | 1-tap preset demo account login | None | `{ email }` | `{ success, user, token }` | `VERIFIED` |
| `POST` | `/auth/forgot-password`| Requests password reset OTP | None | `{ email }` | `{ success, message, demo_otp: "1234" }` | `VERIFIED` |
| `POST` | `/auth/reset-password` | Sets new password with demo OTP | None | `{ email, otp: "1234", new_password }` | `{ success, message }` | `VERIFIED` |
| `POST` | `/auth/refresh` | Generates fresh access token | Refresh Token | `{ refreshToken }` | `{ success, token }` | `VERIFIED` |
| `POST` | `/auth/logout` | Revokes current user session | Bearer JWT | None | `{ success, message }` | `VERIFIED` |

---

## 2. Menstrual Cycle Tracking Endpoints (`/api/v1/cycle`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/cycle/current` | Active cycle phase & days remaining | Bearer JWT | None | `{ success, currentCycle }` | `VERIFIED` |
| `POST` | `/cycle/log` | Records period flow and dates | Bearer JWT | `{ startDate, endDate, flow, symptoms, moods, notes }` | `{ success, log }` | `VERIFIED` |
| `GET` | `/cycle/history` | Historical menstrual records | Bearer JWT | Query: `?limit=10&offset=0` | `{ success, logs }` | `VERIFIED` |
| `GET` | `/cycle/predictions`| Algorithmic cycle phase forecasts | Bearer JWT | None | `{ success, predictions }` | `VERIFIED` |
| `PUT` | `/cycle/settings` | Cycle length & period duration | Bearer JWT | `{ averageCycleLength, averagePeriodLength }` | `{ success, settings }` | `VERIFIED` |
| `DELETE`| `/cycle/log/:id` | Deletes historical period log | Bearer JWT | URL param: `id` | `{ success, message }` | `VERIFIED` |

---

## 3. Trusted Circle & Social Chat Endpoints (`/api/v1/chat`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/chat/conversations` | List of multi-user circle chats | Bearer JWT | None | `{ success, conversations }` | `VERIFIED` |
| `GET` | `/chat/messages/:id` | Messages in a conversation | Bearer JWT | URL param: `recipientId` | `{ success, messages }` | `VERIFIED` |
| `POST` | `/chat/messages` | Sends text message or care item card | Bearer JWT | `{ recipientId, messageText, careProductSnapshot }` | `{ success, message }` | `VERIFIED` |
| `DELETE`| `/chat/messages/:id`| Deletes sent chat message | Bearer JWT | URL param: `id` | `{ success, message }` | `VERIFIED` |
| `GET` | `/chat/quick-items` | Care products for 1-tap chat sharing | Bearer JWT | None | `{ success, items }` | `VERIFIED` |
| `PATCH`| `/chat/contacts/:id/tag`| Assigns relationship tag to contact | Bearer JWT | `{ tag: "HUSBAND" \| "DOCTOR" }` | `{ success, profile }` | `VERIFIED` |
| `GET` | `/chat/search-users` | Discovers registered users by name/email | Bearer JWT | Query: `?q=aman` | `{ success, users }` | `VERIFIED` |

---

## 4. E-Commerce Store & Checkout Endpoints (`/api/v1/store`, `/api/v1/orders`, `/api/v1/payments`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/store/categories` | Store product categories | None | None | `{ success, categories }` | `VERIFIED` |
| `GET` | `/store/products` | Browse store products with filters | None | Query: `?category=&search=&limit=` | `{ success, products }` | `VERIFIED` |
| `GET` | `/store/products/:id`| Full product details | None | URL param: `id` | `{ success, product }` | `VERIFIED` |
| `GET` | `/orders` | Customer order history | Bearer JWT | None | `{ success, orders }` | `VERIFIED` |
| `POST` | `/orders` | Places new customer order | Bearer JWT | `{ addressId, items, isDiscreetPackaging }` | `{ success, order }` | `VERIFIED` |
| `GET` | `/orders/:id` | Order receipt & invoice summary | Bearer JWT | URL param: `id` | `{ success, order }` | `VERIFIED` |
| `POST` | `/payments/razorpay/create`| Initiates Razorpay payment order | Bearer JWT | `{ orderId, amount }` | `{ success, razorpayOrder }` | `VERIFIED` |
| `POST` | `/payments/razorpay/verify`| Validates Razorpay HMAC signature | Bearer JWT | `{ razorpay_order_id, razorpay_payment_id, razorpay_signature }` | `{ success, message }` | `VERIFIED` |
| `POST` | `/payments/demo/success` | Settles order via DemoPaymentProvider | Bearer JWT | `{ orderId, orderNumber }` | `{ success, order, delivery_otp: "4821" }` | `VERIFIED` |

---

## 5. Delivery Agent & Telemetry Endpoints (`/api/v1/deliveries`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/deliveries/agent/dashboard`| Courier pending & active dispatches | Delivery / Admin | None | `{ success, activeDeliveries, stats }` | `VERIFIED` |
| `POST` | `/deliveries/:id/accept` | Courier accepts dispatch order | Delivery / Admin | URL param: `id` | `{ success, delivery }` | `VERIFIED` |
| `POST` | `/deliveries/:id/start` | Courier starts transit | Delivery / Admin | URL param: `id` | `{ success, delivery }` | `VERIFIED` |
| `POST` | `/deliveries/:id/simulate` | Simulates telemetry steps (0-100%) | Delivery / Admin | `{ stepPercent: 50, etaMinutes: 15 }` | `{ success, location }` | `VERIFIED` |
| `POST` | `/deliveries/:id/arrived` | Courier arrives at doorstep | Delivery / Admin | URL param: `id` | `{ success, delivery }` | `VERIFIED` |
| `POST` | `/deliveries/:id/complete`| Validates 4-digit OTP & completes | Delivery / Admin | `{ delivery_otp: "4821" }` | `{ success, message: "Delivered" }` | `VERIFIED` |
| `POST` | `/deliveries/demo/reset` | Resets demo delivery #CC-DEMO-1001 | Delivery / Admin | None | `{ success, message: "Reset complete" }` | `VERIFIED` |
| `GET` | `/orders/:id/tracking` | Recipient live tracking & OTP view | Bearer JWT | URL param: `id` | `{ success, order, courier, delivery_otp }` | `VERIFIED` |

---

## 6. Administrative Control Endpoints (`/api/v1/admin`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/admin/dashboard` | KPI analytics (Users, Orders, Revenue) | `x-admin-key` / Admin | None | `{ success, stats: { totalUsers, realUsersCount, ... } }` | `VERIFIED` |
| `GET` | `/admin/users` | List of all users (Real vs Demo) | `x-admin-key` / Admin | None | `{ success, count, users }` | `VERIFIED` |
| `PATCH`| `/admin/users/:id/tag` | Updates custom user tag | `x-admin-key` / Admin | `{ tag: "VIP ORGANIC MEMBER" }` | `{ success, user }` | `VERIFIED` |
| `PATCH`| `/admin/users/:id/status`| Suspends or activates user | `x-admin-key` / Admin | `{ status: "ACTIVE" \| "SUSPENDED" }` | `{ success, message }` | `VERIFIED` |
| `GET` | `/admin/orders` | Orders management table | `x-admin-key` / Admin | None | `{ success, count, orders }` | `VERIFIED` |
| `PATCH`| `/admin/orders/:id/status`| Updates order fulfillment state | `x-admin-key` / Admin | `{ status: "PACKED", delivery_status }` | `{ success, order }` | `VERIFIED` |
| `GET` | `/admin/products` | Live inventory catalog & stock | `x-admin-key` / Admin | None | `{ success, products }` | `VERIFIED` |
| `GET` | `/admin/deliveries` | Active courier dispatches | `x-admin-key` / Admin | None | `{ success, deliveries }` | `VERIFIED` |
| `GET` | `/admin/chat-logs` | Audits Trusted Circle chat history | `x-admin-key` / Admin | None | `{ success, messages }` | `VERIFIED` |

---

## 7. Shipping Addresses (`/api/v1/addresses`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/addresses` | Saved customer delivery addresses | Bearer JWT | None | `{ success, addresses }` | `VERIFIED` |
| `POST` | `/addresses` | Saves new address with GPS geocode | Bearer JWT | `{ address_line, city, state, pincode, phone, latitude, longitude }` | `{ success, address }` | `VERIFIED` |
| `DELETE`| `/addresses/:id` | Deletes saved delivery address | Bearer JWT | URL param: `id` | `{ success, message }` | `VERIFIED` |

---

## 8. Symptoms & Moods (`/api/v1/symptoms`, `/api/v1/moods`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/symptoms` | Taxonomy of physical symptoms | None | None | `{ success, symptoms }` | `VERIFIED` |
| `POST` | `/symptoms/log` | Logs symptom intensity for date | Bearer JWT | `{ symptomId, severity, logDate }` | `{ success, log }` | `VERIFIED` |
| `GET` | `/moods` | Taxonomy of emotional moods | None | None | `{ success, moods }` | `VERIFIED` |
| `POST` | `/moods/log` | Logs mood score for date | Bearer JWT | `{ moodId, intensity, logDate }` | `{ success, log }` | `VERIFIED` |

---

## 9. Wellness Guides & AI Assistant (`/api/v1/wellness`, `/api/v1/ai`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/wellness/articles` | Educational reproductive health articles | None | Query: `?category=` | `{ success, articles }` | `VERIFIED` |
| `GET` | `/wellness/articles/:id`| Article content and citations | None | URL param: `id` | `{ success, article }` | `VERIFIED` |
| `POST` | `/ai/ask` | CycleCare wellness AI chat query | Bearer JWT | `{ prompt, cycleContext }` | `{ success, response }` | `VERIFIED` |

---

## 10. Partner Care Mode (`/api/v1/partners`)

| Method | Endpoint | Purpose | Auth Required | Request Body / Params | Response Structure | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `POST` | `/partners/invite` | Generates 6-character partner invite code | Bearer JWT | None | `{ success, inviteCode, shareUrl }` | `VERIFIED` |
| `POST` | `/partners/request` | Submits connection request via code | Bearer JWT | `{ inviteCode }` | `{ success, request }` | `VERIFIED` |
| `GET` | `/partners/dashboard`| Displays linked partner cycle phase & moods | Bearer JWT | None | `{ success, partnerProfile, cyclePhase }` | `VERIFIED` |
| `PUT` | `/partners/:id/permissions`| Configures what partner is allowed to see | Bearer JWT | `{ canViewCycle, canViewMoods, canSendGifts }` | `{ success, permissions }` | `VERIFIED` |
| `DELETE`| `/partners/:id` | Revokes partner connection access | Bearer JWT | URL param: `id` | `{ success, message: "Revoked" }` | `VERIFIED` |
