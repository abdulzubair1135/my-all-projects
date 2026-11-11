# 12 - Dashboard Analytics & Reporting Exam Question

## QUESTION
Create an Admin Dashboard Analytics API (`GET /api/dashboard/stats`) that returns overall metrics: total revenue, total bills count, total registered customers, and top 5 best-selling products.

---

## REQUIREMENTS
- Combine aggregate SQL functions (`SUM`, `COUNT`, `GROUP BY`, `ORDER BY DESC LIMIT 5`).
- Protected route requiring `admin` authorization role.

---

## TABLES
`bills`, `customers`, `bill_items`, `products`

---

## FILES REQUIRED
1. `controllers/dashboardController.js`
2. `routes/dashboardRoutes.js`

---

## CODING ORDER
1. Admin authentication check.
2. Query 1: Total Revenue & Total Bills count from `bills`.
3. Query 2: Total Customers count from `customers`.
4. Query 3: Top 5 products by total quantity sold using JOIN on `bill_items` and `products`.

```sql
SELECT p.name, SUM(bi.quantity) AS total_sold 
FROM bill_items bi 
JOIN products p ON bi.product_id = p.id 
GROUP BY bi.product_id 
ORDER BY total_sold DESC 
LIMIT 5;
```

---

## API FLOW
`GET /api/dashboard/stats` -> Execute queries -> Combine stats into JSON object -> Return `200 OK`.

---

## POSTMAN TEST
`GET http://localhost:5000/api/dashboard/stats` Header `Authorization: Bearer <admin_jwt_token>`

---

## COMMON MISTAKES
- Running separate database connections per query instead of executing via pool.
