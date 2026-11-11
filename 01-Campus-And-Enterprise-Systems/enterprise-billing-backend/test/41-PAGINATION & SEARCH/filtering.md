# Dynamic Multi-Field Filtering Guide (`filtering.md`)

Filtering allows clients to filter dataset results by specific field criteria (e.g. `?course=BCA&status=active`).

---

## 1. Dynamic SQL `WHERE` Clause Construction

When parameters are optional, build the `WHERE` clause dynamically by appending conditions and parameter array values.

---

## 2. Dynamic Query Construction Pattern

```javascript
export const getFilteredStudents = async (req, res, next) => {
  try {
    const { course, status, minMarks } = req.query;

    let sql = 'SELECT * FROM students WHERE 1=1';
    const params = [];

    // Filter by Course
    if (course) {
      sql += ' AND course = ?';
      params.push(course);
    }

    // Filter by Status
    if (status) {
      sql += ' AND status = ?';
      params.push(status);
    }

    // Filter by Minimum Marks
    if (minMarks) {
      sql += ' AND marks >= ?';
      params.push(Number(minMarks));
    }

    const [rows] = await pool.query(sql, params);

    res.json({
      success: true,
      message: `Found ${rows.length} matching records`,
      data: rows
    });
  } catch (error) {
    next(error);
  }
};
```

> [!TIP]
> `WHERE 1=1` allows chaining additional `AND ...` conditions cleanly without checking if it is the first condition.
