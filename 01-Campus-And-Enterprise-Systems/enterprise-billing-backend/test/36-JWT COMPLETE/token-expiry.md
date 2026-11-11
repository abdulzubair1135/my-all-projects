# JWT Expiration & Expiry Format Options Guide

## 1. Why Expiration is Critical
Tokens without expiration live forever. If a token is compromised or intercepted, an attacker can access the system indefinitely unless the token expires or is explicitly revoked.

---

## 2. Common `expiresIn` Options in `jsonwebtoken`

| String / Value | Duration |
|----------------|----------|
| `'15m'` | 15 minutes |
| `'1h'` | 1 hour |
| `'1d'` | 1 day |
| `'7d'` | 7 days |
| `3600` | 3600 seconds (1 hour) |

---

## 3. Node.js Example

```js
import jwt from 'jsonwebtoken';

const token = jwt.sign(
  { id: 101, email: "user@example.com" },
  process.env.JWT_SECRET,
  { expiresIn: '1d' } // Expires after 24 hours
);
```

---

## 4. How Expiration is Stored Inside JWT Payload
When `expiresIn` is specified, `jsonwebtoken` automatically adds an `exp` claim to the decoded JSON payload (represented as Unix Timestamp in seconds).

```json
{
  "id": 101,
  "email": "user@example.com",
  "iat": 1786968000,
  "exp": 1787054400
}
```
- `iat`: Issued At (timestamp token was generated).
- `exp`: Expiration timestamp.
