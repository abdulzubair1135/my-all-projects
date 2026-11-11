-- SQL MIN() Aggregate Function Practice

-- 1. Find Lowest Score
SELECT MIN(marks) AS lowest_marks FROM students;

-- 2. Find Earliest Registration Date
SELECT MIN(created_at) AS earliest_registration FROM students;

-- 3. Min Marks by Course
SELECT MIN(marks) AS lowest_bca_marks 
FROM students 
WHERE course = 'BCA';
