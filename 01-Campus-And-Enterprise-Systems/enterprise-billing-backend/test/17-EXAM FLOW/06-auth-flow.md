# Step 06: Authentication & Authorization Flow

BCA practical me JWT (JSON Web Token) aur bcrypt based authentication key requirement hota hai.

---

## 1. Register Flow
```
User sends { name, email, password }
  -> Input Validation (express-validator)
  -> Check if email exists in DB (User.findByEmail)
  -> Hash password with bcrypt.hash(password, 10)
  -> Save user in DB (User.create)
  -> Return success JSON (without plain password!)
```

## 2. Login Flow
```
User sends { email, password }
  -> Input Validation
  -> Check if email exists in DB (User.findByEmail)
  -> Compare password with bcrypt.compare(password, user.password)
  -> Generate JWT Token with jwt.sign({ id, role, email }, secret, { expiresIn: '1d' })
  -> Return token in standard success response
```

## 3. Protected Route Flow
```
Client sends request with Header: Authorization: Bearer <TOKEN>
  -> Auth Middleware intercepts request
  -> Extracts token from "Authorization" header
  -> Verifies token with jwt.verify(token, secret)
  -> Attaches decoded user data to req.user
  -> Calls next() to proceed to Controller
```
