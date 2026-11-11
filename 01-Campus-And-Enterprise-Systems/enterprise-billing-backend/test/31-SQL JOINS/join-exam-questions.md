# SQL Joins Exam & Viva Questions Guide

## Question 1: What is the main difference between `INNER JOIN` and `LEFT JOIN`?
- **Answer**:
  - `INNER JOIN` returns only the matching rows present in **both** tables. Non-matching rows from either table are excluded.
  - `LEFT JOIN` returns **all** rows from the left table, plus matched rows from the right table. If no match exists on the right side, columns from the right table are filled with `NULL`.

---

## Question 2: What is the difference between `LEFT JOIN` and `RIGHT JOIN`?
- **Answer**:
  - `LEFT JOIN` prioritizes all rows from the left table.
  - `RIGHT JOIN` prioritizes all rows from the right table.
  - `s LEFT JOIN d ON s.dept_id = d.id` produces identical results to `d RIGHT JOIN s ON d.id = s.dept_id`.

---

## Question 3: What causes `Error: Column 'id' in field list is ambiguous` in SQL?
- **Answer**:
  - This occurs when both joined tables contain a column with the exact same name (e.g. `id`), and the `SELECT` query requests `SELECT id ...` without specifying which table's column to pick.
  - **Fix**: Use table prefixes or aliases like `SELECT s.id, d.id FROM ...`.

---

## Question 4: How can you find rows in Table A that have no matching entry in Table B?
- **Answer**:
  - By performing a `LEFT JOIN` and filtering where the primary key of Table B `IS NULL`.
  ```sql
  SELECT a.* 
  FROM table_a a 
  LEFT JOIN table_b b ON a.id = b.a_id 
  WHERE b.id IS NULL;
  ```
