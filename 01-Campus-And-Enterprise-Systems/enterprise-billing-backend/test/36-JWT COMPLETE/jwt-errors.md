# JWT Errors & Exception Handling Guide

## 1. Common JWT Exceptions Thrown by `jwt.verify()`

| Error Name | Cause | Typical HTTP Response |
|------------|-------|-----------------------|
| **`TokenExpiredError`** | Token current time is past `exp` claim | `401 Unauthorized` |
| **`JsonWebTokenError`** | Invalid signature, invalid algorithm, or malformed payload | `403 Forbidden` / `401 Unauthorized` |
| **`NotBeforeError`** | Current time is before `nbf` claim | `403 Forbidden` |

---

## 2. Handling JWT Errors in Express Catch Blocks

```js
import jwt from 'jsonwebtoken';

try {
  const decoded = jwt.verify(token, process.env.JWT_SECRET);
} catch (err) {
  if (err instanceof jwt.TokenExpiredError) {
    return res.status(401).json({
      success: false,
      message: "Token has expired",
      error: "TOKEN_EXPIRED",
      expiredAt: err.expiredAt
    });
  }
  
  if (err instanceof jwt.JsonWebTokenError) {
    return res.status(403).json({
      success: false,
      message: "Invalid token signature or malformed token",
      error: "INVALID_TOKEN"
    });
  }

  return res.status(500).json({
    success: false,
    message: "Failed to authenticate token",
    error: err.message
  });
}
```

---

## 3. Exam Viva Question
- **Q**: What causes `JsonWebTokenError: invalid signature`?
- **A**: This occurs when the secret key used to verify the token (`jwt.verify`) does not match the secret key used when signing the token (`jwt.sign`), or if any character in the token payload was tampered with by the client.
