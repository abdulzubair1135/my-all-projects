-- SQL AVG() Aggregate Function Practice

-- 1. Calculate Average Marks
SELECT AVG(marks) AS average_marks FROM students;

-- 2. Average Rounded to 2 Decimal Places
SELECT ROUND(AVG(marks), 2) AS rounded_avg_marks FROM students;

-- 3. Average for Specific Course
SELECT ROUND(AVG(marks), 2) AS bca_average 
FROM students 
WHERE course = 'BCA';
