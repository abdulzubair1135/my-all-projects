# 05 - CORS Error

## ERROR
Browser console shows: `Access to fetch at 'http://localhost:5000/api' from origin 'http://localhost:3000' has been blocked by CORS policy`.

---

## WHY IT HAPPENS
Browser blocks cross-origin HTTP requests when frontend domain/port differs from backend domain/port, unless backend explicitly includes CORS headers.

---

## HOW TO FIND IT
- Appears in Browser Console or Postman pre-flight checks.

---

## HOW TO FIX IT
1. Install `cors` package:
```bash
npm install cors
```
2. Enable CORS in `server.js`:
```javascript
import cors from 'cors';
import express from 'express';

const app = express();
app.use(cors()); // Allow all origins for exam testing
```

---

## COMMON EXAM MISTAKE
Placing `app.use(cors())` *after* defining API routes in `server.js`. `cors()` middleware MUST be registered *before* routes!
