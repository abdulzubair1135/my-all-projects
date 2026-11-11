# Securing Express HTTP Headers with `helmet` (`helmet.md`)

`helmet` is a security middleware for Express.js that secures your web application by setting various HTTP headers. It helps protect against common web vulnerabilities like Cross-Site Scripting (XSS), Clickjacking, MIME sniffing, and Information Disclosure.

---

## 1. Installation

```bash
npm install helmet
```

---

## 2. Express Setup Example

```javascript
import express from 'express';
import helmet from 'helmet';

const app = express();

// Enable standard security headers
app.use(helmet());
```

---

## 3. Key Headers Set by `helmet`

| Header | Protective Purpose |
| :--- | :--- |
| `X-Content-Type-Options: nosniff` | Prevents browsers from MIME-sniffing a response away from the declared content-type. |
| `X-Frame-Options: SAMEORIGIN` | Prevents Clickjacking by disabling your site from being embedded inside iframe tags. |
| `Strict-Transport-Security` | Enforces HTTPS connections (HSTS). |
| `X-DNS-Prefetch-Control` | Controls browser DNS prefetching behavior. |
| `X-Powered-By` (Removed) | Removes the default `X-Powered-By: Express` header so attackers cannot fingerprint the technology stack. |

---

## 4. Disabling `X-Powered-By` Manually

Even without helmet, always hide Express framework signature:
```javascript
app.disable('x-powered-by');
```
