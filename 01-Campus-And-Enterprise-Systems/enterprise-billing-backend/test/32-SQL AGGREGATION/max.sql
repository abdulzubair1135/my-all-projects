-- SQL MAX() Aggregate Function Practice

-- 1. Find Highest Score across entire table
SELECT MAX(marks) AS highest_marks FROM students;

-- 2. Find Highest Score in BCA
SELECT MAX(marks) AS top_bca_score 
FROM students 
WHERE course = 'BCA';
