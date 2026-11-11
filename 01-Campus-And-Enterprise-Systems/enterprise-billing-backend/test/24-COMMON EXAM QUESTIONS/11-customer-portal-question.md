# 11 - Customer Portal API Exam Question

## QUESTION
Create a Customer Portal API allowing logged-in customers to view their own purchase history and aggregate total spent.

---

## REQUIREMENTS
- Enforce customer data privacy: Customers can ONLY see their OWN bills (`WHERE customer_id = req.user.id`).
- Return list of bills along with sum total spent across all bills.

---

## TABLES
```sql
CREATE TABLE bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    grand_total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## FILES REQUIRED
1. `controllers/customerController.js`
2. `routes/customerRoutes.js`

---

## CODING ORDER
1. Add route `GET /api/customer/my-bills` protected with `authenticateToken`.
2. Extract customer ID from `req.user.id`.
3. Perform SQL query: `SELECT * FROM bills WHERE customer_id = ?`.
4. Perform aggregate SQL query: `SELECT SUM(grand_total) AS total_spent FROM bills WHERE customer_id = ?`.

---

## API FLOW
`GET /api/customer/my-bills` Header: `Authorization: Bearer <customer_token>` -> Fetch customer bills -> Return JSON response.

---

## POSTMAN TEST
`GET http://localhost:5000/api/customer/my-bills` Header `Authorization: Bearer <customer_jwt_token>`

---

## COMMON MISTAKES
- Reading `customer_id` from URL parameter `/bills/:customerId` instead of logged-in user token `req.user.id`, allowing customers to view other users' data.
