# JSON Web Token (JWT) Creation Guide (`jwt.sign`)

## 1. What is a JWT?
JSON Web Token (JWT) is an open standard (RFC 7519) that defines a compact, self-contained way for securely transmitting information between parties as a JSON object.

---

## 2. Structure of a JWT
A JWT string consists of 3 parts separated by dots (`.`):
`Header.Payload.Signature`

1. **Header**: Defines algorithm and token type (`{"alg": "HS256", "typ": "JWT"}`).
2. **Payload**: Contains claims/data (`{"userId": 1, "role": "admin"}`).
3. **Signature**: Cryptographic signature generated using `Header + Payload + Secret Key`.

---

## 3. Node.js Code Example (ES Modules)

```js
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
dotenv.config();

export const generateToken = (userId, role) => {
  const payload = { id: userId, role };
  const secretKey = process.env.JWT_SECRET || 'fallback_exam_secret';
  const options = { expiresIn: '1h' }; // Expires in 1 hour

  const token = jwt.sign(payload, secretKey, options);
  return token;
};
```
