-- SQL Update Statements Practice

-- CAUTION: Always use WHERE clause in UPDATE statements to avoid modifying all table rows!

-- 1. Update Single Column for Specific Record
UPDATE students 
SET marks = 95 
WHERE id = 1;

-- 2. Update Multiple Columns for Specific Record
UPDATE students 
SET name = 'Rahul Dev Sharma', course = 'MCA', marks = 90 
WHERE id = 1;

-- 3. Conditional Batch Update
UPDATE students 
SET marks = marks + 5 
WHERE course = 'BCA';

-- 4. Node.js Parameterized Query Pattern:
-- UPDATE students SET name = ?, course = ?, marks = ? WHERE id = ?;
