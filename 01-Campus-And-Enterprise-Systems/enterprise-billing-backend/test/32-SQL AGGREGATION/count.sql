-- SQL COUNT() Aggregate Function Practice

-- 1. Count Total Number of Rows in Table
SELECT COUNT(*) AS total_students FROM students;

-- 2. Count Non-Null Values in Specific Column
SELECT COUNT(email) AS registered_emails FROM students;

-- 3. Count Unique / Distinct Values
SELECT COUNT(DISTINCT course) AS unique_courses_count FROM students;

-- 4. Count with WHERE Filter
SELECT COUNT(*) AS bca_student_count 
FROM students 
WHERE course = 'BCA';
