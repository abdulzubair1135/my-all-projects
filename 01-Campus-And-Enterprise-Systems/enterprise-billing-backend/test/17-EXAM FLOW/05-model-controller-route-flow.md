# Step 05: Model-Controller-Route (MCR) Flow

Backend Architecture MVC pattern (without View rendering) follow karta hai for REST API creation.

---

## Architecture Flow Diagram
```
Client Request -> Express Server -> Route (Validation + Auth Middleware) -> Controller -> Model (MySQL Query) -> Controller -> Standard JSON Response
```

---

## Role Breakdown

1. **Model (`models/*.js`):**
   - Pure Database Queries (`pool.query(...)`).
   - SQL queries parameterize hoti hain (`?` placeholders).
   - Returns raw JS objects or database result rows.

2. **Controller (`controllers/*.controller.js`):**
   - Business Logic handle karta hai.
   - Validation errors check karta hai (`validationResult(req)`).
   - Model functions invoke karta hai.
   - Standard response send karta hai (`sendSuccess`, `sendError`).

3. **Routes (`routes/*.routes.js`):**
   - Endpoint URL (`/api/users`, `/api/auth/login`) define karta hai.
   - HTTP Methods (`GET`, `POST`, `PUT`, `DELETE`) map karta hai.
   - Middlewares (Validation + Auth JWT check) mount karta hai.

4. **Server Entry (`server.js`):**
   - Express App initialize karta hai (`const app = express()`).
   - Middleware load karta hai (`express.json()`, `cors()`).
   - Routes attach karta hai (`app.use('/api/...', routes)`).
   - Global Error Handling middleware configure karta hai.
   - App start/listen on `process.env.PORT`.
