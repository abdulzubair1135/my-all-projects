# Step 02: Identify Requirements & Scope

Question paper padhte hi exact requirements ko shortlist aur breakdown karna hai.

---

## 1. Functional Requirements Checklist
- [ ] **Database Connection:** Connect Node.js app with MySQL database using `mysql2/promise`.
- [ ] **User Management / Auth:**
  - Register API (`POST /api/auth/register`)
  - Login API (`POST /api/auth/login`)
  - Profile / Protected route (`GET /api/auth/me`)
- [ ] **Core Business Entity CRUD (e.g. Products / Users / Franchises):**
  - Create (`POST /api/resource`)
  - Read All (`GET /api/resource`)
  - Read Single (`GET /api/resource/:id`)
  - Update (`PUT /api/resource/:id`)
  - Delete (`DELETE /api/resource/:id`)
- [ ] **Complex Workflow (e.g. POS / Billing):**
  - Cart calculation / Total price + tax logic.
  - Insert bill metadata and line items in DB.
- [ ] **Validation & Error Handling:**
  - Input field validation using `express-validator`.
  - Global error handling middleware for handling unexpected server errors.

---

## 2. Non-Functional / Coding Standards Requirements
- Standard response format:
  ```json
  {
    "success": true,
    "message": "Operation successful",
    "data": { ... }
  }
  ```
- Environment variable configuration (`.env` with `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `PORT`, `JWT_SECRET`).
- Security practices: Hashed passwords with `bcrypt`, token signature with `jsonwebtoken`, SQL injection prevention with parameterized queries (`pool.query(sql, [params])`).
