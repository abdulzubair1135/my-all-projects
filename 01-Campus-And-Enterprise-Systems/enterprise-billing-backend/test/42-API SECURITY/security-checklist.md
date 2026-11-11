# Node.js & Express REST API Security Checklist (`security-checklist.md`)

Use this comprehensive security checklist during practical exams and real-world project code reviews to ensure maximum protection.

---

## 1. Authentication & Session Security
- [ ] Passwords are hashed using `bcrypt` with at least 10 salt rounds.
- [ ] Plaintext passwords are never logged or stored in database tables.
- [ ] JWT tokens are signed using strong secrets stored in `.env` (`process.env.JWT_SECRET`).
- [ ] JWT expiration times (`expiresIn: '1d'`) are set.
- [ ] Sensitive passwords/hashes are excluded from user response payloads.

## 2. Input Validation & Sanitization
- [ ] All `req.body`, `req.params`, and `req.query` inputs are validated using `express-validator`.
- [ ] String inputs are trimmed (`.trim()`) and escaped (`.escape()`) to prevent XSS.
- [ ] Param strings are parsed into numbers (`.toInt()`) for primary keys.

## 3. Database Security & SQL Injection
- [ ] All database queries use parameterized placeholders `?` with `mysql2/promise`.
- [ ] No dynamic SQL strings are constructed via concatenation.
- [ ] Sorting columns and order keywords (`ASC`/`DESC`) are checked against whitelists.

## 4. HTTP Headers & Middleware
- [ ] `helmet()` middleware is mounted to enforce security headers.
- [ ] Express signature header is disabled (`app.disable('x-powered-by')`).
- [ ] `cors()` middleware is configured to restrict unauthorized domain origins.
- [ ] `express-rate-limit` is configured to block DDoS and brute-force attacks.

## 5. File Upload Protection
- [ ] Uploaded file size limits are enforced (`limits: { fileSize: 2MB }`).
- [ ] Uploaded file MIME types are validated against allowed image/document formats.
- [ ] Custom unique filenames are generated to prevent overwrite attacks.

## 6. Environment & Configuration
- [ ] Database credentials and secrets reside in `.env`.
- [ ] `.env` is listed in `.gitignore`.
- [ ] Direct stack traces are hidden in production environments.
