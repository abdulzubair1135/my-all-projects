# REST API Pagination Guide (`pagination.md`)

Pagination breaks large datasets into smaller, manageable chunks or pages. Instead of fetching thousands of records at once (which degrades memory and database performance), pagination returns a fixed subset per request.

---

## 1. Key Pagination Concepts

- **Page (`page`)**: The current target page number (1-based index: 1, 2, 3...).
- **Limit (`limit`)**: The number of items to return per page (e.g. 10 items per page).
- **Total Records (`totalRecords`)**: The total number of matching rows in the database.
- **Total Pages (`totalPages`)**: Calculated as `Math.ceil(totalRecords / limit)`.

---

## 2. Standard Paginated API Response Contract

```json
{
  "success": true,
  "message": "Students list retrieved",
  "data": [
    { "id": 11, "name": "Rahul Sharma", "course": "BCA" },
    { "id": 12, "name": "Priya Patel", "course": "BCA" }
  ],
  "pagination": {
    "currentPage": 2,
    "limit": 10,
    "totalRecords": 45,
    "totalPages": 5,
    "hasNextPage": true,
    "hasPrevPage": true
  }
}
```

---

## 3. Mathematical Calculations

1. **Calculating SQL `OFFSET`**:
   $$\text{offset} = (\text{page} - 1) \times \text{limit}$$
   - Page 1, Limit 10 $\rightarrow \text{Offset} = 0$ (Items 1 to 10)
   - Page 2, Limit 10 $\rightarrow \text{Offset} = 10$ (Items 11 to 20)

2. **Calculating `totalPages`**:
   $$\text{totalPages} = \lceil \frac{\text{totalRecords}}{\text{limit}} \rceil$$
