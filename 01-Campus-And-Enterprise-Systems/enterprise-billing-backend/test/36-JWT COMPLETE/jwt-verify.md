# JWT Verification Guide (`jwt.verify`)

## 1. How Does Token Verification Work?
When a client sends a request to a protected API endpoint, the server inspects the JWT token attached in the request header using `jwt.verify(token, secretKey)`.

If the signature is valid and the token has not expired, `jwt.verify` decodes and returns the original payload. If invalid or expired, it throws an error.

---

## 2. Node.js Code Example (ES Modules)

```js
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
dotenv.config();

export const verifyJwtToken = (token) => {
  try {
    const secretKey = process.env.JWT_SECRET || 'fallback_exam_secret';
    // Decodes and validates signature + expiration
    const decoded = jwt.verify(token, secretKey);
    return { valid: true, decoded };
  } catch (error) {
    return { valid: false, error: error.message };
  }
};
```
