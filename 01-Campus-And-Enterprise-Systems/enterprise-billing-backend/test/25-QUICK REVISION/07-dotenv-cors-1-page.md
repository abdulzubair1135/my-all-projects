# Dotenv & CORS One-Page Quick Revision Sheet

## 1. Dotenv Setup (`.env`)
Environment variables keep sensitive parameters (DB credentials, secret keys) out of source code.

### `.env` File Content
```env
PORT=5000
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=secret
DB_NAME=exam_db
JWT_SECRET=super_secret_jwt_key
```

### Loading `.env` in Code
```javascript
import dotenv from 'dotenv';
dotenv.config();

console.log(process.env.PORT); // 5000
```
*Note: Call `dotenv.config()` at the very top of your app before referencing `process.env`!*

---

## 2. CORS Setup (`cors`)
Allows requests from external origins / cross-domain clients.

```javascript
import cors from 'cors';
import express from 'express';

const app = express();
app.use(cors()); // Allow all cross-origin requests for testing
```
