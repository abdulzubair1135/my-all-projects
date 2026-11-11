# Query Parameters (`req.query`) Guide

## 1. What are Query Parameters?
Query parameters appear after the `?` symbol in a URL. Multiple parameters are separated by `&`. They are optional parameters primarily used for filtering, searching, sorting, and pagination.

---

## 2. Structure & URL Formatting Example
```
URL: http://localhost:5000/api/products?category=electronics&minPrice=500&sort=asc
Parsed req.query:
{
  category: "electronics",
  minPrice: "500",
  sort: "asc"
}
```

---

## 3. Express Code Example (ES Modules)

```js
import express from 'express';
const app = express();

app.get('/api/products', (req, res) => {
  // Destructure query parameters with fallback default values
  const { category, minPrice, page = 1, limit = 10 } = req.query;

  const pageNum = parseInt(page, 10);
  const limitNum = parseInt(limit, 10);
  const minPriceNum = minPrice ? parseFloat(minPrice) : 0;

  res.status(200).json({
    success: true,
    data: {
      filters: { category: category || 'all', minPrice: minPriceNum },
      pagination: { page: pageNum, limit: limitNum }
    }
  });
});
```

---

## 4. Differences: `req.params` vs `req.query` (Exam Question)

| Feature | `req.params` | `req.query` |
|---------|--------------|-------------|
| **URL Placement** | Part of URL path (`/users/5`) | After `?` in URL (`/users?id=5`) |
| **Requirement** | Mandatory for route matching | Optional key-value pairs |
| **Primary Use** | Identify specific resource | Filter, sort, paginate resources |
| **Example** | `GET /students/10` | `GET /students?gender=female` |
