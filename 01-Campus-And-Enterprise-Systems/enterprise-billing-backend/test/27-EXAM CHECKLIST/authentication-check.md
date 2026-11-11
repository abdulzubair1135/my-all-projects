# Authentication & Security Checklist

## Auth Security Checklist

- [ ] **Password Hashing**: Passwords stored in database start with `$2b$10$` (Bcrypt hash).
- [ ] **No Plain Text Passwords**: Database inserts never store un-hashed passwords.
- [ ] **JWT Payload**: JWT contains `id`, `email`, and `role` claims, excluding password hash.
- [ ] **Token Expiration**: Token has explicit lifespan defined (`expiresIn: '24h'`).
- [ ] **Protected Routes**: Middleware verifies `Authorization: Bearer <token>` on secured routes.
- [ ] **Role-Based Access (RBAC)**: Admin routes verify `req.user.role === 'admin'` and block non-admins with 403 Forbidden.
