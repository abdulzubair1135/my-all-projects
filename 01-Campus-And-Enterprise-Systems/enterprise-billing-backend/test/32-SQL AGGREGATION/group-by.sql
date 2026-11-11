-- SQL GROUP BY Practice

-- 1. Group Students Count by Course
SELECT 
    course, 
    COUNT(*) AS total_students 
FROM students 
GROUP BY course;

-- 2. Group By with Multiple Aggregation Functions
SELECT 
    course, 
    COUNT(*) AS total_students,
    ROUND(AVG(marks), 2) AS avg_marks,
    MAX(marks) AS max_marks,
    MIN(marks) AS min_marks
FROM students 
GROUP BY course;

-- 3. Group By with ORDER BY
SELECT 
    course, 
    AVG(marks) AS avg_marks 
FROM students 
GROUP BY course 
ORDER BY avg_marks DESC;
