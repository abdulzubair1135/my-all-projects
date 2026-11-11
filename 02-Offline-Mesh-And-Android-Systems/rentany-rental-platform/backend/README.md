# RentAny Production API Server

This is the secure, production-grade REST API backend server for **RentAny** — the Peer-to-Peer Neighborhood Rental Marketplace application.

It is built with Node.js, Express.js, and MySQL. It features JWT access/refresh token rotation, comprehensive input validation, transaction-safe booking checks, spatial-proximity listing searches, and an administrative control panel.

---

## 🛠️ Technology Stack

* **Runtime**: Node.js (ES Modules syntax)
* **Framework**: Express.js
* **Database**: MySQL 8.0+
* **Authentication**: JWT (JSON Web Tokens) with refresh token rotation and revocation
* **Security**: Helmet, CORS, and Express Rate Limiting
* **Input Validation**: Express Validator
* **Media Storage**: Multer (Local disk storage)

---

## 📂 Project Structure

```text
rentany-backend/
├── src/
│   ├── config/             # Environment variables, DB pool, and security policies
│   │   ├── database.js
│   │   ├── env.js
│   │   └── security.js
│   ├── controllers/        # Express handlers processing HTTP requests
│   │   ├── admin.controller.js
│   │   ├── auth.controller.js
│   │   ├── booking.controller.js
│   │   ├── category.controller.js
│   │   ├── chat.controller.js
│   │   ├── listing.controller.js
│   │   ├── notification.controller.js
│   │   ├── review.controller.js
│   │   ├── user.controller.js
│   │   └── wishlist.controller.js
│   ├── db/                 # SQL schemas, migration scripts, and seed data
│   │   ├── migrate.js
│   │   ├── schema.sql
│   │   └── seed.js
│   ├── middleware/         # Auth verification, rate limiters, error catches
│   │   ├── admin.middleware.js
│   │   ├── auth.middleware.js
│   │   ├── error.middleware.js
│   │   ├── rateLimit.middleware.js
│   │   ├── upload.middleware.js
│   │   └── validation.middleware.js
│   ├── repositories/       # Encapsulated database raw SQL queries
│   │   ├── banner.repository.js
│   │   ├── booking.repository.js
│   │   ├── chat.repository.js
│   │   ├── listing.repository.js
│   │   ├── notification.repository.js
│   │   ├── review.repository.js
│   │   ├── user.repository.js
│   │   └── wishlist.repository.js
│   ├── routes/             # REST route mapping for modules
│   │   ├── index.js
│   │   ├── auth.routes.js
│   │   ├── user.routes.js
│   │   ├── category.routes.js
│   │   ├── listing.routes.js
│   │   ├── booking.routes.js
│   │   ├── review.routes.js
│   │   ├── wishlist.routes.js
│   │   ├── chat.routes.js
│   │   ├── notification.routes.js
│   │   ├── admin.routes.js
│   │   └── compatibility.routes.js
│   ├── services/           # Business logic (pricing calculations, transactional booking check)
│   │   ├── auth.service.js
│   │   ├── booking.service.js
│   │   ├── payment.service.js
│   │   ├── pricing.service.js
│   │   └── search.service.js
│   ├── app.js              # Express app middleware configuration
│   └── server.js           # Server listen entrypoint
├── uploads/                # Stores uploaded images
├── tests/                  # Mocha & Supertest integration tests
├── .env.example
├── package.json
└── README.md
```

---

## 🚀 Getting Started (Local Development)

### 1. Prerequisites
Make sure you have [Node.js](https://nodejs.org/) (v16+) and a [MySQL 8.0](https://www.mysql.com/) server running locally.

### 2. Install Dependencies
Clone the repository, navigate to the `/backend` folder, and install packages:
```bash
npm install
```

### 3. Setup Environment Variables
Copy `.env.example` to a new file named `.env` and fill in your MySQL server credentials:
```env
PORT=5000
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=rentany

JWT_ACCESS_SECRET=your_jwt_access_secret_key
JWT_REFRESH_SECRET=your_jwt_refresh_secret_key
```

### 4. Build Database Schema & Seed Data
Execute the migration tool to automatically create the `rentany` database, set up foreign keys, index performance optimization fields, and seed starting items matching the mobile app catalog:
```bash
npm run db:init
```

### 5. Launch the Server
Start the development server:
```bash
npm start
```
The server will boot up at **`http://localhost:5000`**.

---

## 📲 Backward Compatibility (Android Client Sync)

We have implemented a **backwards-compatibility layer** mounted directly under `/api/...`. This matches the unauthenticated structures expected by the mobile client's Retrofit interfaces (`RentApiService.kt`).

* It automatically redirects profile, items, bookings, chats, and settings sync requests.
* Operations are default-mapped to the main developer profile (`Rohan Patel`, user ID: 1).
* Key names are dynamically translated (e.g. `price_per_day` is mapped to `pricePerDay`) so the Room database parser on the Kotlin client does not crash.

Simply configure the Android app's Backend Base URL to: **`http://<your-local-ip>:5000`** (or your deployed server domain).

---

## 🧪 Integration Testing

We have built a test suite using Mocha and Supertest. It includes automatic database liveness checks: if MySQL is offline on your local machine, it runs public route tests and skips DB-dependent test cases instead of crashing.

To run the test suite:
```bash
npm test
```

Tested scenarios include:
* Registration, logins, and invalid passwords.
* Unique credential limits.
* Listing creations and ownership protections (User A cannot edit User B's listing).
* Geolocation distance boundary filtering (Haversine formula).
* Transaction-safe bookings (double-booking date clashes are rejected).
* Admin role enforcement (regular users cannot view administrative stats).

---

## 📂 Postman Collection
Import the pre-configured API endpoints from:
[`rentany_postman_collection.json`](file:///c:/rentANY/backend/rentany_postman_collection.json)

It includes pre-populated JSON bodies for user registrations, login sessions, listing publishing, booking requests, chatting, and admin dashboard KPI tracking.

---

## 🔒 Security Implementations

1. **Strict SQL Parameterization**: No raw concatenations. All queries execute through connection pools using placeholder bindings (`?`) protecting against SQL Injection.
2. **Double-Booking Protection**: Dates are locked at transactional levels in MySQL using `SELECT ... FOR UPDATE` before confirming dates.
3. **Password Protection**: Passwords are saved as securely salted hashes using `bcryptjs`.
4. **Header Sanitization**: Express Helmet is loaded to secure HTTP headers.
5. **Rate Limiting**: Limits logins to 15 attempts per 15 minutes, preventing brute force dictionary hacks.
6. **JWT Rotation & Revocation**: Short-lived access tokens (15m) combined with rotational refresh tokens stored in the database.
7. **Address Privacy**: Geolocation calculations return coordinates and distances, but exact street addresses are omitted in public searches, revealing them only on confirmed booking tickets.
