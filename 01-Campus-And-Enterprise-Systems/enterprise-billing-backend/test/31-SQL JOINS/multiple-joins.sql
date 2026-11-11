-- Multiple Table JOINS Practice (3+ Tables)

-- Schema Assumption:
-- students: id, name, department_id
-- departments: id, dept_name
-- enrollments: id, student_id, course_id, grade
-- courses: id, course_title, credits

SELECT 
    s.id AS student_id,
    s.name AS student_name,
    d.dept_name,
    c.course_title,
    e.grade
FROM students s
INNER JOIN departments d ON s.department_id = d.id
INNER JOIN enrollments e ON s.id = e.student_id
INNER JOIN courses c ON e.course_id = c.id
ORDER BY s.name ASC;
