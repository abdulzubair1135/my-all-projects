# 04 - Franchise Management Exam Question

## QUESTION
Build a Multi-Franchise Management API allowing Admins to register franchises, list franchises by city, update franchise operational status (`active`/`inactive`), and view total sales revenue per franchise.

---

## REQUIREMENTS
- Endpoints:
  - `POST /api/franchises` (Create new franchise)
  - `GET /api/franchises` (Filter by city query param: `?city=Delhi`)
  - `PUT /api/franchises/:id/status` (Update active status)
  - `GET /api/franchises/:id/sales` (Aggregate sales revenue from bills table)

---

## TABLES
```sql
CREATE TABLE franchises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active'
);
```

---

## FILES REQUIRED
1. `config/db.js`
2. `controllers/franchiseController.js`
3. `routes/franchiseRoutes.js`
4. `server.js`

---

## CODING ORDER
1. Setup DB Schema.
2. Create Franchise Controller with SQL filter logic (`WHERE city = ?`).
3. Add status update endpoint logic.
4. Mount routes in Express application.

---

## API FLOW
`GET /api/franchises?city=Delhi` -> `pool.query('SELECT * FROM franchises WHERE city = ?', [city])` -> Return JSON list.

---

## POSTMAN TEST
- `POST http://localhost:5000/api/franchises` Body: `{"name": "South Hub", "code": "FR-DEL-02", "owner_name": "Suresh", "city": "Delhi"}`
- `GET http://localhost:5000/api/franchises?city=Delhi`

---

## COMMON MISTAKES
- Not handling optional query parameters (`city` parameter missing in query string).
