# 08 - Role-Based Access Control (RBAC) Exam Question

## QUESTION
Implement Role-Based Authorization where public users can view products, logged-in staff can create products, but ONLY users with `role === 'admin'` can delete products or view revenue reports.

---

## REQUIREMENTS
- Middleware function `authorizeRoles(...roles)` that checks `req.user.role`.
- Return `403 Forbidden` if user does not possess required role.

---

## TABLES
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'staff', 'customer') DEFAULT 'customer'
);
```

---

## FILES REQUIRED
1. `middleware/authMiddleware.js` (JWT authentication & RBAC check middleware)
2. `routes/productRoutes.js`

---

## CODING ORDER
1. Implement JWT auth middleware `authenticateToken`.
2. Implement role middleware helper:
```javascript
export const authorizeRoles = (...allowedRoles) => {
    return (req, res, next) => {
        if (!req.user || !allowedRoles.includes(req.user.role)) {
            return res.status(403).json({
                success: false,
                message: 'Forbidden: You do not have permission to perform this action'
            });
        }
        next();
    };
};
```
3. Protect routes: `router.delete('/:id', authenticateToken, authorizeRoles('admin'), deleteProduct)`.

---

## API FLOW
`DELETE /api/products/1` -> `authenticateToken` validates JWT -> `authorizeRoles('admin')` checks `req.user.role` -> `deleteProduct` executes.

---

## POSTMAN TEST
- Login as customer/staff -> Attempt DELETE -> Expect `403 Forbidden`.
- Login as admin -> Attempt DELETE -> Expect `200 OK`.

---

## COMMON MISTAKES
- Putting `authorizeRoles` before `authenticateToken` in route definition (`req.user` will be undefined!).
