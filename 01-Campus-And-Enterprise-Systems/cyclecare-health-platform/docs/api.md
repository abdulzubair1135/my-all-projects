# CycleCare REST API Specification

## Base URL
`/api/v1`

## Headers
- `Content-Type: application/json`
- `Authorization: Bearer <JWT_TOKEN>`

## Endpoints Summary

### Authentication (`/auth`)
- `POST /auth/register` - Create user account
- `POST /auth/login` - Authenticate & retrieve JWT tokens
- `POST /auth/logout` - Invalidate session
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Request password reset token
- `POST /auth/reset-password` - Update password with token

### User Profile (`/me`)
- `GET /me` - Retrieve authenticated user profile & cycle settings
- `PATCH /me` - Update display name or cycle settings
- `DELETE /me` - Request account deletion (GDPR/Privacy compliance)

### Cycle Management (`/cycle`)
- `GET /cycle` - Fetch period logs & settings
- `POST /cycle/period` - Add period log entry
- `PATCH /cycle/period/:id` - Update existing log entry
- `DELETE /cycle/period/:id` - Remove period log entry
- `GET /cycle/calendar` - Fetch monthly calendar events (periods, symptoms, moods, user events)
- `GET /cycle/history` - Fetch historical cycle metrics (cycle length, period length, trends)
- `GET /cycle/prediction` - Calculate next period estimation window
- `GET /cycle/insights` - Generate automated wellness summary insights

### Symptoms & Moods (`/symptoms`, `/moods`)
- `GET /symptoms` - List catalog of trackable symptoms
- `POST /symptoms/log` - Record symptom log
- `GET /symptoms/history` - Retrieve recorded symptom history
- `DELETE /symptoms/log/:id` - Delete symptom log
- `GET /moods` - List catalog of moods
- `POST /moods/log` - Record mood log
- `GET /moods/history` - Retrieve recorded mood history

### Reminders (`/reminders`)
- `GET /reminders` - Retrieve user reminder configurations
- `POST /reminders` - Create new reminder
- `PATCH /reminders/:id` - Update reminder toggle or schedule
- `DELETE /reminders/:id` - Delete reminder

### Store & Cart (`/categories`, `/products`, `/cart`, `/wishlist`)
- `GET /categories` - List active product categories
- `GET /products` - Search & filter catalog products
- `GET /products/:id` - Product details, stock state, and reviews
- `GET /wishlist` - View user wishlist
- `POST /wishlist` - Add item to wishlist
- `DELETE /wishlist/:id` - Remove item from wishlist
- `GET /cart` - Retrieve current cart items & calculated total
- `POST /cart/items` - Add item to cart
- `PATCH /cart/items/:id` - Update quantity
- `DELETE /cart/items/:id` - Remove item from cart

### Orders & Payments (`/orders`, `/payments`, `/coupons`)
- `POST /orders` - Create new order from cart
- `GET /orders` - List user orders
- `GET /orders/:id` - View order status & item details
- `POST /orders/:id/cancel` - Cancel pending order
- `POST /payments/create` - Generate payment gateway order (Razorpay)
- `POST /payments/verify` - Server-side HMAC signature verification
- `POST /payments/webhook` - Async payment gateway webhook processing
- `POST /coupons/validate` - Server-side coupon verification

### Care Kits & Restock (`/care-kits`, `/restock`)
- `GET /care-kits` - List user care kits
- `POST /care-kits` - Save custom care kit
- `POST /care-kits/:id/buy` - Move kit items to cart
- `GET /restock` - Get tracked restock items & low-supply alerts
- `PATCH /restock/:id` - Update item quantity remaining

### AI Wellness Assistant (`/ai`)
- `POST /ai/chat` - Interact with "Ask CycleCare" educational AI assistant

### Admin Panel (`/admin`)
- `GET /admin/dashboard` - Platform metrics, total orders, revenue, active users
- `GET /admin/users` - View registered users
- `PATCH /admin/users/:id/status` - Enable/Disable user account
- `GET /admin/products` & `POST /admin/products` - Manage product catalog & inventory
- `GET /admin/orders` & `PATCH /admin/orders/:id/status` - Order fulfillment & state transitions
- `GET /admin/audit-logs` - System audit log audit trail
