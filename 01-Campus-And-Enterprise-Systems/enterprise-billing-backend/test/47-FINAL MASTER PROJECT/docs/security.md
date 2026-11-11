# Master Project Security & Data Integrity

## Security Implementation Highlights

### 1. Password Hashing
- Utilizes `bcryptjs` with salt round factor of `10`.
- Ensures plain-text passwords are never stored in the database.

### 2. Authentication & Authorization
- **Stateless Tokens:** JSON Web Tokens (JWT) signed with a secret key.
- **RBAC (Role-Based Access Control):** Restricts administrative actions (e.g., category creation, product mutations) strictly to users with `role: 'admin'`.

### 3. Protection Against Injection Attacks
- **SQL Injection Prevention:** All SQL statements in models utilize parameterized queries (`pool.query(sql, [params])`). No string concatenation is used for user inputs.

### 4. Input Validation & Sanitization
- `express-validator` validates parameters, request body schemas, and data types before passing control to controllers.

### 5. HTTP Security Headers & CORS
- `helmet` adds key security headers to prevent XSS, clickjacking, and mime-type sniffing.
- `cors` configures cross-origin resource sharing.

### 6. Database ACIDs & Transactions
- Order checkout wraps product stock validation, order header creation, and line-item creation inside an atomic MySQL transaction (`beginTransaction`, `commit`, `rollback`).
