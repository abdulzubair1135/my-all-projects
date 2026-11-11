# 01 - Product CRUD Operations Exam Question

## QUESTION
Create a RESTful API in Node.js, Express, and MySQL for managing products. Implement full CRUD functionality (Create, Read All, Read Single, Update, Delete) using ES Modules, parameterized queries, and express-validator.

---

## REQUIREMENTS
- Database table `products` with columns `id`, `name`, `category`, `price`, `stock`.
- Endpoints:
  - `GET /api/products` (Fetch all products)
  - `GET /api/products/:id` (Fetch single product)
  - `POST /api/products` (Create product with validation)
  - `PUT /api/products/:id` (Update product)
  - `DELETE /api/products/:id` (Delete product)

---

## TABLES
```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## FILES REQUIRED
1. `.env`
2. `config/db.js`
3. `controllers/productController.js`
4. `routes/productRoutes.js`
5. `middleware/productValidation.js`
6. `server.js`

---

## CODING ORDER
1. Create Database & Table in MySQL.
2. Initialize `package.json` with `"type": "module"`.
3. Create `.env` & `config/db.js` database connection pool.
4. Create `middleware/productValidation.js`.
5. Create `controllers/productController.js` with CRUD methods.
6. Create `routes/productRoutes.js`.
7. Assemble app in `server.js` and test.

---

## API FLOW
1. **CREATE**: `POST /api/products` -> Validation Middleware -> Controller `pool.query('INSERT INTO products ...')` -> Return `201 Created`.
2. **READ ALL**: `GET /api/products` -> Controller `pool.query('SELECT * FROM products')` -> Return `200 OK`.
3. **READ BY ID**: `GET /api/products/:id` -> Controller check exists -> Return `200 OK` or `404 Not Found`.
4. **UPDATE**: `PUT /api/products/:id` -> Controller `pool.query('UPDATE products SET ... WHERE id = ?')` -> Return `200 OK`.
5. **DELETE**: `DELETE /api/products/:id` -> Controller `pool.query('DELETE FROM products WHERE id = ?')` -> Return `200 OK`.

---

## POSTMAN TEST
- `POST http://localhost:5000/api/products` Body: `{"name": "Mouse", "category": "IT", "price": 500, "stock": 10}`
- `GET http://localhost:5000/api/products`
- `PUT http://localhost:5000/api/products/1` Body: `{"name": "Mouse Pro", "category": "IT", "price": 600, "stock": 15}`
- `DELETE http://localhost:5000/api/products/1`

---

## COMMON MISTAKES
- Returning un-parsed MySQL array output directly instead of array destructuring `const [rows] = await pool.query(...)`.
- Forgetting `express.json()` middleware in `server.js`.
