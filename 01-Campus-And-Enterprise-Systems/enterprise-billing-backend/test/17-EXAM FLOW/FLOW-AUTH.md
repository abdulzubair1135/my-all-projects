# Master Summary Flow: Authentication Project

Authentication and Authorization architecture flow using JWT and Bcrypt.

---

## 1. File & Component Breakdown
```
19-AUTHENTICATION PROJECT/
├── config/
│   └── db.js
├── controllers/
│   ├── register.controller.js
│   └── login.controller.js
├── helpers/
│   ├── password.helper.js
│   └── jwt.helper.js
├── middleware/
│   └── auth.middleware.js
├── models/
│   └── User.js
├── routes/
│   └── auth.routes.js
├── validation/
│   └── auth.validation.js
├── .env.example
├── package.json
├── README.md
└── server.js
```

---

## 2. Key Steps & Flow
1. **Password Hashing:** `bcrypt.hash(plainText, 10)` in `helpers/password.helper.js`.
2. **Password Verification:** `bcrypt.compare(plainText, hash)` in `helpers/password.helper.js`.
3. **JWT Sign:** `jwt.sign(payload, secret, { expiresIn: '1d' })` in `helpers/jwt.helper.js`.
4. **JWT Auth Middleware:** Extract token from `Authorization: Bearer <token>`, verify token, attach `req.user`, or return `401 Unauthorized`.
5. **Registration Controller:** Validate request -> Check if user exists -> Hash password -> Insert DB -> Return 201 Created.
6. **Login Controller:** Validate request -> Find user by email -> Compare password -> Generate Token -> Return Token & User profile.
