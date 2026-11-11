# SET 05 - Search, Filtering & Pagination

## Question
Implement Search, Filter by Category, and Offset Pagination (`page`, `limit`) for a Product Catalog API.

---

## Requirements
1. Endpoint `GET /api/products` accepts query parameters:
   - `search`: Keyword to search inside product `title` (using `LIKE %keyword%`).
   - `category`: Filter products by category.
   - `page`: Page number (default: 1).
   - `limit`: Number of items per page (default: 10).
2. Calculate `offset = (page - 1) * limit`.
3. Return pagination info: `totalItems`, `totalPages`, `currentPage`, `limit`.

---

## Solution Code

### `controllers/productController.js`
```javascript
import pool from '../config/db.js';

export const getProducts = async (req, res) => {
  try {
    let { search = '', category = '', page = 1, limit = 10 } = req.query;
    page = parseInt(page);
    limit = parseInt(limit);
    const offset = (page - 1) * limit;

    let whereClause = 'WHERE 1=1';
    let params = [];

    if (search) {
      whereClause += ' AND title LIKE ?';
      params.push(`%${search}%`);
    }
    if (category) {
      whereClause += ' AND category = ?';
      params.push(category);
    }

    // Count Total Matching Records
    const [countResult] = await pool.query(`SELECT COUNT(*) as total FROM products ${whereClause}`, params);
    const totalItems = countResult[0].total;

    // Fetch Paginated Rows
    const dataSql = `SELECT * FROM products ${whereClause} ORDER BY id DESC LIMIT ? OFFSET ?`;
    const [rows] = await pool.query(dataSql, [...params, limit, offset]);

    res.json({
      success: true,
      message: 'Products retrieved',
      pagination: {
        totalItems,
        totalPages: Math.ceil(totalItems / limit),
        currentPage: page,
        limit
      },
      data: rows
    });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Server error', error: err.message });
  }
};
```

---

## Postman Test Guide
- `GET http://localhost:5000/api/products?search=laptop&page=1&limit=5`
