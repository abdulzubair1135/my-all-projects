-- LEFT JOIN (or LEFT OUTER JOIN) Practice

-- LEFT JOIN: Returns all records from the left table (students),
-- and matching records from the right table (departments).
-- If no match exists, NULL values are returned for right table columns.

SELECT 
    s.id AS student_id,
    s.name AS student_name,
    s.email,
    COALESCE(d.dept_name, 'Unassigned') AS department_name
FROM students s
LEFT JOIN departments d ON s.department_id = d.id;

-- Find students who are NOT assigned to any department (NULL check):
SELECT 
    s.id,
    s.name,
    s.email
FROM students s
LEFT JOIN departments d ON s.department_id = d.id
WHERE d.id IS NULL;
