-- SQL Select Statements Practice

-- 1. Select All Columns from Table
SELECT * FROM students;

-- 2. Select Specific Columns (Recommended for performance)
SELECT id, name, email, course FROM students;

-- 3. Select with Column Aliases (AS keyword)
SELECT 
    id AS student_id, 
    name AS student_name, 
    marks AS score 
FROM students;

-- 4. Select Distinct Values (Unique Courses)
SELECT DISTINCT course FROM students;

-- 5. Select with Calculated Column
SELECT name, marks, (marks + 5) AS updated_marks_with_grace FROM students;
