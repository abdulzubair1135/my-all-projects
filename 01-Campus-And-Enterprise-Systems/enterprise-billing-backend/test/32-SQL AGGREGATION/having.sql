-- SQL HAVING Clause Practice

-- Difference between WHERE and HAVING (Exam Priority Question):
-- WHERE filters individual rows BEFORE aggregation.
-- HAVING filters aggregated groups AFTER GROUP BY execution.

-- 1. Show Courses having more than 5 enrolled students
SELECT 
    course, 
    COUNT(*) AS student_count 
FROM students 
GROUP BY course 
HAVING COUNT(*) > 5;

-- 2. Show Courses where Average Marks is greater than 75
SELECT 
    course, 
    ROUND(AVG(marks), 2) AS avg_marks 
FROM students 
GROUP BY course 
HAVING AVG(marks) > 75.0;

-- 3. Combining WHERE, GROUP BY, HAVING, ORDER BY together
SELECT 
    course, 
    AVG(marks) AS avg_marks 
FROM students 
WHERE marks >= 40                -- Step 1: Filter individual passing students
GROUP BY course                 -- Step 2: Group by course
HAVING AVG(marks) >= 70         -- Step 3: Filter groups with course average >= 70
ORDER BY avg_marks DESC;        -- Step 4: Sort results
