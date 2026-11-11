# 13 - Route 404 Not Found Error

## ERROR
Postman returns `404 Not Found` HTML page or `{ "message": "Cannot GET /api/product" }`.

---

## WHY IT HAPPENS
1. Typo in URL path in Postman (e.g. `/api/product` vs `/api/products`).
2. HTTP method mismatch (e.g. sending `POST` to a route defined as `router.get()`).
3. Route prefix mismatch in `server.js` (`app.use('/api/v1/products', productRoutes)` vs request to `/api/products`).

---

## HOW TO FIND IT
- Compare exact request method (`GET`/`POST`/`PUT`/`DELETE`) and URL path in Postman with `server.js` and route files.

---

## HOW TO FIX IT
1. Verify route registration in `server.js`:
```javascript
import productRoutes from './routes/productRoutes.js';
app.use('/api/products', productRoutes);
```
2. Verify path inside `productRoutes.js`:
```javascript
router.get('/', getProducts);     // Maps to GET /api/products
router.get('/:id', getProductById); // Maps to GET /api/products/1
```
3. Add a global 404 catch-all handler in `server.js`:
```javascript
app.use((req, res) => {
    res.status(404).json({
        success: false,
        message: `Cannot ${req.method} ${req.originalUrl}`
    });
});
```

---

## COMMON EXAM MISTAKE
Writing full path inside route file like `router.get('/api/products', getProducts)` when path `/api/products` was already prefixed in `app.use('/api/products', productRoutes)` inside `server.js`. That creates route `/api/products/api/products`!
