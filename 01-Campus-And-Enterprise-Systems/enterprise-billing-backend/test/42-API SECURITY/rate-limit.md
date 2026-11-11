# Rate Limiting with `express-rate-limit` (`rate-limit.md`)

Rate limiting restricts the number of requests a client (IP address) can make to your server within a defined window of time. It protects APIs from Denial of Service (DDoS) attacks, brute-force login attempts, and resource abuse.

---

## 1. Installation

```bash
npm install express-rate-limit
```

---

## 2. General API Rate Limiter Setup

```javascript
import express from 'express';
import rateLimit from 'express-rate-limit';

const app = express();

// General API limiter (e.g., max 100 requests per 15 minutes per IP)
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  standardHeaders: true, // Return rate limit info in `RateLimit-*` headers
  legacyHeaders: false, // Disable `X-RateLimit-*` headers
  message: {
    success: false,
    message: 'Too many requests from this IP. Please try again after 15 minutes.',
    error: 'TOO_MANY_REQUESTS'
  }
});

// Apply global rate limiter to all API routes
app.use('/api/', globalLimiter);
```

---

## 3. Strict Rate Limiter for Authentication Routes

Sensitive routes like `/api/auth/login` require stricter rate limits to block dictionary brute-force attacks:

```javascript
// Strict auth limiter (e.g. max 5 login attempts per 10 minutes)
export const authLimiter = rateLimit({
  windowMs: 10 * 60 * 1000, // 10 minutes
  max: 5, // Limit to 5 requests per IP
  message: {
    success: false,
    message: 'Too many failed login attempts. Please try again in 10 minutes.',
    error: 'BRUTE_FORCE_PREVENTION'
  }
});

// Usage in login route
app.post('/api/auth/login', authLimiter, loginController);
```
