# 08_DATA_FLOW_AND_BUSINESS_LOGIC.md — Data Flow Traces and Business Logic

**Scope:** Step-by-step lifecycle traces of core business processes, algorithmic calculations, validation rules, state transitions, and error handling in CycleCare.  
**Audit Date:** 2026-10-10  
**Evidence Standard:** Traced from Android Activities/ViewModels through Retrofit, Express routes, controllers, services, database queries, and UI state updates.

---

## 1. Menstrual Cycle Prediction & Health Data Flow

### 1.1 Complete Lifecycle Trace
1. **User Input:** User opens `PeriodLogActivity.java`, selects Start Date (`2026-10-01`), End Date (`2026-10-05`), Flow Intensity (`Heavy`), and Symptom chips (`Cramps`, `Headache`).
2. **Local Room Insertion:** Tapping *[ Save Log ]* executes `PeriodLogDao.insert(entity)` with status `PENDING_SYNC` and enqueues payload in `sync_queue`.
3. **HTTP Dispatch:** `CycleRepository` posts to `POST /api/v1/cycle/log` with JWT Bearer token in headers.
4. **Backend Route & Controller:** `cycleRoutes.js` passes request to `cycleController.logPeriod()`.
5. **Database Mutation:** Query builder executes `INSERT INTO period_logs (user_id, start_date, end_date, flow, symptoms, notes) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`.
6. **Prediction Engine (`cycleService.js`):**
   - Retrieves `average_cycle_length` (e.g. 28 days) and `average_period_length` (e.g. 5 days) from `cycle_settings`.
   - **Menstrual Phase:** Day 1 to Day `average_period_length`.
   - **Follicular Phase:** Day `average_period_length + 1` to Day `average_cycle_length - 15`.
   - **Ovulation Window:** Day `average_cycle_length - 14` (±2 days).
   - **Luteal Phase:** Day `average_cycle_length - 11` to Day `average_cycle_length`.
7. **Client Refresh:** `HomeFragment.onResume()` fetches latest active estimation or queries local Room DB. Dynamic thermostat dial renders *Day 12 of 28 (42%)* and *16 days left - Ovulation Window*.

---

## 2. Store Order, Checkout & Inventory Lifecycle

### 2.1 Complete Lifecycle Trace
1. **Catalog Browsing:** User adds *CycleCare Bamboo Pads* (Quantity: 2) in `StoreFragment.java`.
2. **Cart Steppers:** `CartActivity.java` updates in-memory `CartItem` quantity; calculates Subtotal (₹558.00), Delivery Fee (₹0.00), Total (₹558.00).
3. **Checkout Selection:** User selects shipping address in `CheckoutActivity.java` and enables *Discreet Packaging*.
4. **Payment Options:**
   - **Option A (Razorpay Gateway):** Calls `POST /api/v1/payments/razorpay/create`. Razorpay SDK opens mobile checkout modal. Upon success, client posts signature to `/api/v1/payments/razorpay/verify`.
   - **Option B (Demo Payment Flow):** Calls `POST /api/v1/payments/demo/success` with `{ orderId }`.
5. **Backend Settlement (`paymentsController.js`):**
   - Updates `orders` table: `payment_status = 'PAID'`, `order_status = 'READY_FOR_DELIVERY'`, `delivery_status = 'READY_FOR_DELIVERY'`.
   - Assigns confidential 4-digit recipient OTP: `delivery_otp = '4821'`.
   - Generates inventory movement record: `INSERT INTO inventory_movements (product_id, quantity, movement_type, notes) VALUES ($1, -2, 'PURCHASE', 'Order payment completed')`.
   - Decrements stock in `products` table: `UPDATE products SET stock = stock - 2 WHERE id = $1`.
   - Inserts delivery dispatch record: `INSERT INTO deliveries (order_id, status, delivery_otp) VALUES ($1, 'READY_FOR_DELIVERY', '4821')`.
6. **UI State Update:** Mobile client navigates to `OrderDetailActivity.java`, displaying confirmation badge and 4-digit OTP card.

---

## 3. Trusted Circle Real-Time Chat & Care Sharing Flow

### 3.1 Complete Lifecycle Trace
1. **Inbox Selection:** User selects *Aman Sharma (Husband)* in `CircleConversationsActivity.java`.
2. **Direct Chat (`CircleChatActivity.java`):** Fetches history via `GET /api/v1/chat/messages/:id`.
3. **Care Item Sharing:** User taps *[ + Care Product ]* pill. Bottom sheet `dialog_care_item_sheet.xml` lists catalog items (`GET /api/v1/chat/quick-items`). User selects *Organic Heating Cramp Patch*.
4. **Message Mutation:** Android client executes `POST /api/v1/chat/messages` with payload:
   ```json
   {
     "recipientId": "10f31e6e-cbb7-465d-b820-8b215b74852e",
     "messageText": "Could you please bring this home today? ❤️",
     "careProductSnapshot": {
       "id": "8ee034d3-e1d2-4875-b9f1-0e0b2b5fa066",
       "name": "Organic Heating Cramp Patch",
       "price": 249.00,
       "image_url": "https://..."
     }
   }
   ```
5. **Database Storage:** Node.js inserts record into `circle_messages` with snapshot details.
6. **Chat Stream Rendering:** `ChatAdapter.java` renders incoming/outgoing bubble with embedded interactive care card. Tapping *[ View & Buy ]* opens `ProductDetailActivity.java`.
7. **Message Deletion:** User long-presses sent message bubble; client calls `DELETE /api/v1/chat/messages/:id`. Backend removes row from `circle_messages` and updates Recycler item.

---

## 4. Courier Dispatch, Telemetry & OTP Verification Flow

### 4.1 Complete Lifecycle Trace
1. **Dispatch Initiation:** Courier logs into `DeliveryAgentActivity.java` (using `delivery.demo@cyclecare.app`). Pending order #CC-DEMO-1001 is retrieved via `GET /api/v1/deliveries/agent/dashboard`.
2. **Accept & Pickup:** Courier taps *[ Accept Delivery ]* (`POST /api/v1/deliveries/:id/accept`) and *[ Picked Up ]* (`POST /api/v1/deliveries/:id/pickup`).
3. **In Transit Simulation:** Courier taps *[ Start Delivery ]* (`POST /api/v1/deliveries/:id/start`). Tapping *[ Simulate Movement ]* increments progress percent (25% -> 50% -> 75% -> 90%) and posts telemetry updates (`POST /api/v1/deliveries/:id/simulate`).
4. **Recipient Live Map View (`OrderTrackingActivity.java`):** Customer views courier marker moving on map, live ETA decreasing (15 min), and confidential OTP badge (`4821`).
5. **Arrival:** Courier taps *[ Arrived ]* (`POST /api/v1/deliveries/:id/arrived`).
6. **OTP Handover:** Courier asks recipient for verbal OTP. Recipient provides `4821`.
7. **Verification & Completion:** Courier enters `4821` in *[ Complete Delivery ]* dialog. Client posts `POST /api/v1/deliveries/:id/complete` with `{ delivery_otp: "4821" }`.
8. **Authoritative Gate:**
   - If OTP matches: Backend sets `deliveries.status = 'DELIVERED'`, `orders.status = 'DELIVERED'`, `orders.delivery_status = 'DELIVERED'`, and `delivered_at = NOW()`.
   - If OTP mismatch: Backend returns `HTTP 400 { success: false, message: "Invalid delivery OTP" }`.
9. **Synchronized UI Result:** Both Courier dashboard and Recipient tracking screen immediately reflect completed delivery status.

---

## 5. Administrative Control Oversight & User Tagging Flow

### 5.1 Complete Lifecycle Trace
1. **Admin Login:** Admin opens `start_control_panel.bat`, which launches `http://localhost:5000/admin-panel/admin.html` with key `8c2e54885f922a59917e38d497e970aaa25287fe99a2e3fd`.
2. **Dashboard Query:** `admin.html` queries `GET /api/v1/admin/dashboard` and `GET /api/v1/admin/users`.
3. **Real vs Demo Segregation:**
   - If user is organic: Displayed with `REAL USER` badge, total lifetime orders, and green status pill.
   - If user is seed account: Displayed with `DEMO` badge.
4. **Tag Customization:** Admin clicks *[ Tag ]* on user row; enters `VIP ORGANIC MEMBER` or `HUSBAND`. Admin panel executes `PATCH /api/v1/admin/users/:id/tag` with `{ tag: "VIP ORGANIC MEMBER" }`.
5. **Persistence:** Controller updates `profiles.account_tag = $1`. The change is immediately visible in the Android Trusted Circle list, Chat header pill, and Admin users table.
