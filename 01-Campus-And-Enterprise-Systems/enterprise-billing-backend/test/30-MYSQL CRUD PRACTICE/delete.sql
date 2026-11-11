-- SQL Delete Statements Practice

-- CAUTION: Always use WHERE clause in DELETE statements unless clearing entire table!

-- 1. Delete Specific Record by ID
DELETE FROM students 
WHERE id = 3;

-- 2. Conditional Delete
DELETE FROM students 
WHERE marks < 40;

-- 3. Clear All Records (DML Delete vs DDL Truncate)
-- DELETE FROM students; -- Deletes all rows, logs row operations, retains AUTO_INCREMENT counter
-- TRUNCATE TABLE students; -- Resets table and AUTO_INCREMENT counter back to 1

-- 4. Node.js Parameterized Query Pattern:
-- DELETE FROM students WHERE id = ?;
