-- SQL SUM() Aggregate Function Practice

-- 1. Calculate Sum of Column Values
SELECT SUM(marks) AS total_marks_all_students FROM students;

-- 2. Sum with WHERE Condition
SELECT SUM(marks) AS bca_total_marks 
FROM students 
WHERE course = 'BCA';
