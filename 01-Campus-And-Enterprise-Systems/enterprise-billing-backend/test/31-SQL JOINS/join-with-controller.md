# Express Controller with MySQL JOIN Operations

## 1. Overview
This guide demonstrates how to execute SQL `JOIN` queries inside Express controllers using `mysql2/promise` with parameterized inputs and ES Modules syntax.

---

## 2. Complete Express Route & Controller Example

```js
// db.js - Database Pool Config
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
dotenv.config();

export const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'test_db',
  waitForConnections: true,
  connectionLimit: 10
});

// studentController.js
import { pool } from './db.js';

// GET /api/students-with-dept?deptId=1
export const getStudentsWithDepartment = async (req, res) => {
  try {
    const { deptId } = req.query;

    let sql = `
      SELECT 
        s.id AS student_id,
        s.name AS student_name,
        s.email,
        d.id AS dept_id,
        d.dept_name,
        d.location
      FROM students s
      INNER JOIN departments d ON s.department_id = d.id
    `;
    
    const params = [];

    if (deptId) {
      sql += ` WHERE d.id = ?`;
      params.push(parseInt(deptId, 10));
    }

    sql += ` ORDER BY s.id DESC`;

    const [rows] = await pool.query(sql, params);

    res.status(200).json({
      success: true,
      message: "Fetched students with department details successfully",
      data: rows
    });
  } catch (error) {
    console.error("Join Controller Error:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch student details",
      error: error.message
    });
  }
};
```

---

## 3. Best Practices for Exams
1. Always use table aliases (`s` for students, `d` for departments) to avoid column ambiguity error (`Column 'id' in field list is ambiguous`).
2. Alias returned primary keys clearly (`s.id AS student_id`, `d.id AS dept_id`) so data isn't overwritten in JS objects.
