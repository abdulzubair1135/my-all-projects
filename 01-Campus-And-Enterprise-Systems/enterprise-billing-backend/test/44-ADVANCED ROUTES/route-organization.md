# Express Route Modularization & Clean Architecture Guide (`route-organization.md`)

As REST API applications scale, placing all route definitions in `server.js` leads to unmaintainable code. Organizing routes modularly promotes separation of concerns and maintainability.

---

## 1. Directory Architecture Pattern

```text
src/
├── config/
│   └── db.js                 # MySQL Pool Connection
├── controllers/
│   ├── auth.controller.js    # Auth business logic
│   └── student.controller.js # Student business logic
├── middleware/
│   ├── auth.middleware.js    # JWT & Role validation
│   └── validate.middleware.js# express-validator handler
├── routes/
│   ├── index.js              # Central Master Router
│   ├── public.routes.js      # Login, Register
│   ├── protected.routes.js   # Student Profile
│   └── admin.routes.js       # Admin Operations
└── server.js                 # Express Application Entrypoint
```

---

## 2. Central Router (`routes/index.js`)

Combine all modular router modules into a single entrypoint router:

```javascript
import express from 'express';
import publicRoutes from './public.routes.js';
import protectedRoutes from './protected.routes.js';
import adminRoutes from './admin.routes.js';

const router = express.Router();

// Mount Feature Modules with Clean Path Prefixes
router.use('/public', publicRoutes);
router.use('/user', protectedRoutes);
router.use('/admin', adminRoutes);

export default router;
```

---

## 3. Server Entrypoint Connection (`server.js`)

```javascript
import express from 'express';
import apiRouter from './routes/index.js';

const app = express();
app.use(express.json());

// Mount Master API Router
app.use('/api', apiRouter);

app.listen(5000, () => console.log('Server running on port 5000'));
```
