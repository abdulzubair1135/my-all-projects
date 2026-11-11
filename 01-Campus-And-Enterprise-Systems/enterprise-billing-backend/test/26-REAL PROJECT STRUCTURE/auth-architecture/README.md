# Authentication & RBAC Architecture Blueprint

## Overview
Architecture specialized for security, role-based access control, JWT verification, and bcrypt hashing.

---

## Directory Diagram

```
auth-architecture/
├── .env
├── server.js
├── config/
│   └── db.js
├── middleware/
│   ├── authMiddleware.js        # Verifies Bearer JWT token
│   ├── roleMiddleware.js        # Checks req.user.role against allowed roles
│   └── validatorMiddleware.js   # Sanitizes and validates request bodies
├── controllers/
│   ├── authController.js        # Login & Register handlers
│   └── adminController.js       # Admin-only dashboard handlers
└── routes/
    ├── authRoutes.js
    └── adminRoutes.js
```
