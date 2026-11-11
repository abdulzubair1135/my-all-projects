# HTTP Bearer Token Format Guide

## 1. Authorization Header Format
The standard convention for sending JWT tokens over HTTP is via the `Authorization` header using the `Bearer` scheme.

### Header Structure:
```http
Authorization: Bearer <JWT_TOKEN_STRING>
```

---

## 2. Extracting Bearer Token in Express

```js
const authHeader = req.headers['authorization'];

if (!authHeader || !authHeader.startsWith('Bearer ')) {
  return res.status(401).json({
    success: false,
    message: "Access denied. No bearer token provided.",
    error: "TOKEN_MISSING"
  });
}

// Split by space and pick token string at index 1
const token = authHeader.split(' ')[1];
```

---

## 3. Postman Configuration for Testing
In Postman:
1. Navigate to the **Authorization** tab.
2. Select Type: **Bearer Token**.
3. Paste token string into the Token input field.
