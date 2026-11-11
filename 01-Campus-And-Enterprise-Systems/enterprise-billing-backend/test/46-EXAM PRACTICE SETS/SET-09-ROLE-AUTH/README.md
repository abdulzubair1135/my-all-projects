# SET 09 - Role-Based Access Control (RBAC)

## Question
Write a reusable role authorization middleware function `authorizeRoles(...roles)` that checks user roles extracted from a JWT token.

---

## Requirements
1. Extract user payload (`req.user`) attached by `verifyToken` middleware.
2. Accept allowed roles array e.g., `authorizeRoles('admin', 'superadmin')`.
3. Return `403 Forbidden` if user's role is not included in the allowed roles list.

---

## Solution Code

### `middleware/roleMiddleware.js`
```javascript
export const authorizeRoles = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user || !req.user.role) {
      return res.status(401).json({ success: false, message: 'Unauthorized access' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: `Forbidden. Role '${req.user.role}' is not authorized to access this resource.`
      });
    }

    next();
  };
};
```

### `routes/adminRoutes.js`
```javascript
import express from 'express';
import { verifyToken } from '../middleware/authMiddleware.js';
import { authorizeRoles } from '../middleware/roleMiddleware.js';

const router = express.Router();

// Only Admin can access
router.delete('/users/:id', verifyToken, authorizeRoles('admin'), deleteUser);
```
