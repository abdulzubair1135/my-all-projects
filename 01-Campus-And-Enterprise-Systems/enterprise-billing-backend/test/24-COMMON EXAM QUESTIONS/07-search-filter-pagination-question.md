# 07 - Search, Filter & Pagination Exam Question

## QUESTION
Create an endpoint `GET /api/products` that supports live keyword search (`?search=mouse`), category filter (`?category=IT`), sorting (`?sortBy=price&order=ASC`), and page pagination (`?page=1&limit=10`).

---

## REQUIREMENTS
- Calculate offset: `const offset = (page - 1) * limit`.
- Support total page count calculation using `COUNT(*)`.

---

## TABLES
```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

---

## FILES REQUIRED
1. `controllers/productController.js`
2. `routes/productRoutes.js`
3. `server.js`

---

## CODING ORDER
1. Extract query params in controller (`const { search, category, page = 1, limit = 10 } = req.query`).
2. Build SQL conditions dynamically (`WHERE 1=1 AND name LIKE ?`).
3. Execute SQL query with `LIMIT ? OFFSET ?`.

---

## API FLOW
`GET /api/products?search=mouse&page=1&limit=5` -> Dynamically construct SQL -> Fetch total count & paginated rows -> Return response containing `page`, `totalPages`, `data`.

---

## POSTMAN TEST
`GET http://localhost:5000/api/products?search=wireless&category=Electronics&page=1&limit=2`

---

## COMMON MISTAKES
- Passing string parameters directly to `LIMIT ? OFFSET ?` in MySQL. Cast `page` and `limit` to integers (`parseInt(limit, 10)`).
