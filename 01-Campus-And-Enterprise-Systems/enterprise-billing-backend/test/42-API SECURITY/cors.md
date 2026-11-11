# Configuring CORS in Express (`cors.md`)

Cross-Origin Resource Sharing (CORS) is a security mechanism that allows or restricts web applications running at one domain (e.g. `http://localhost:3000`) from making API requests to another domain (e.g. `http://localhost:5000`).

---

## 1. Installation

```bash
npm install cors
```

---

## 2. Basic vs Production Setup

### Basic (Allow All Origins - Dev Mode Only)
```javascript
import express from 'express';
import cors from 'cors';

const app = express();

// Allow all cross-origin requests (Dev mode only)
app.use(cors());
```

### Production Setup (Restricted Domain Whitelist)
```javascript
import cors from 'cors';

const allowedOrigins = ['http://localhost:3000', 'https://mycollegeportal.com'];

const corsOptions = {
  origin: (origin, callback) => {
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Blocked by CORS policy: Origin not allowed'));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true, // Allow cookies/auth headers across domains
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));
```
