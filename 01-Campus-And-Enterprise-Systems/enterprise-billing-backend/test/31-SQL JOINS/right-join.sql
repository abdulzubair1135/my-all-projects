-- RIGHT JOIN (or RIGHT OUTER JOIN) Practice

-- RIGHT JOIN: Returns all records from the right table (departments),
-- and matched records from the left table (students).
-- If no match exists, NULL values are returned for left table columns.

SELECT 
    d.id AS dept_id,
    d.dept_name,
    s.id AS student_id,
    s.name AS student_name
FROM students s
RIGHT JOIN departments d ON s.department_id = d.id;

-- Find departments that have NO students enrolled:
SELECT 
    d.id AS dept_id,
    d.dept_name
FROM students s
RIGHT JOIN departments d ON s.department_id = d.id
WHERE s.id IS NULL;
