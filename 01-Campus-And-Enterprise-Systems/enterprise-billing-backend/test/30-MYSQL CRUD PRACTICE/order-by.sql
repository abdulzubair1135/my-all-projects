-- SQL ORDER BY Sorting Practice

-- 1. Sort Ascending (Default: ASC)
SELECT * FROM students 
ORDER BY marks ASC;

-- 2. Sort Descending (Highest marks first)
SELECT * FROM students 
ORDER BY marks DESC;

-- 3. Sort Alphabetically by Name
SELECT * FROM students 
ORDER BY name ASC;

-- 4. Sort by Multiple Columns (Primary sort by course ASC, Secondary sort by marks DESC)
SELECT * FROM students 
ORDER BY course ASC, marks DESC;
