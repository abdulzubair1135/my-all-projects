# 404 Not Found Error Guide (`404-errors.md`)

The `404 Not Found` HTTP status code indicates that the server cannot find the requested resource or route path.

---

## 1. When to Return HTTP 404

1. **Undefined URL Endpoint**: The route requested by the client does not exist on the server (e.g. `GET /api/nonexistent`).
2. **Missing Resource in DB**: The client requested a specific database record by ID (e.g. `GET /api/students/999`), but no record matches that ID.

---

## 2. Standard 404 Response Format

```json
{
  "success": false,
  "message": "Student record with ID 999 not found",
  "error": "NOT_FOUND"
}
```

---

## 3. Database Check Controller Example

```javascript
export const getStudentById = async (req, res, next) => {
  try {
    const [rows] = await pool.query('SELECT * FROM students WHERE id = ?', [req.params.id]);
    
    if (rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: `Student with ID ${req.params.id} does not exist`,
        error: 'RESOURCE_NOT_FOUND'
      });
    }

    res.status(200).json({
      success: true,
      message: 'Student record found',
      data: rows[0]
    });
  } catch (error) {
    next(error);
  }
};
```
