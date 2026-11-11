# Postman API Testing Guide for Practical Exams

## Quick Start
This folder contains standardized JSON templates for testing Express.js API endpoints in Postman during backend exams.

---

## Testing Workflow Order in Practical Exams

1. **Step 1: Register User** (`01-register.json`)
   - Send `POST` to `/api/auth/register` with JSON body.
   - Verify `201 Created` status response.

2. **Step 2: Login & Copy Token** (`02-login.json`)
   - Send `POST` to `/api/auth/login`.
   - Copy the JWT `token` string returned in response.

3. **Step 3: Test Protected Endpoint** (`08-protected-route.json`)
   - Paste token in Headers: `Authorization: Bearer <token>` or Authorization Tab -> Type: Bearer Token.

4. **Step 4: Execute CRUD Requests**
   - `03-get-all.json` -> `GET /api/products`
   - `04-get-by-id.json` -> `GET /api/products/1`
   - `05-create.json` -> `POST /api/products`
   - `06-update.json` -> `PUT /api/products/1`
   - `07-delete.json` -> `DELETE /api/products/1`

5. **Step 5: Test Negative Scenarios**
   - `09-invalid-token.json` -> Send request with bad token, expect `401 Unauthorized`.
   - `10-validation-error.json` -> Send invalid payload, expect `400 Bad Request`.

---

## Important Headers Checklist
- `Content-Type: application/json` for `POST` / `PUT` requests with JSON body.
- `Authorization: Bearer <token>` for endpoints using JWT authentication middleware.
