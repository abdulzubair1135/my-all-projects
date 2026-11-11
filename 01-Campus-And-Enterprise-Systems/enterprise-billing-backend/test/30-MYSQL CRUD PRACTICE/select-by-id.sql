-- SQL Select By Primary Key (ID) Practice

-- 1. Select Single Record by Primary Key
SELECT id, name, email, course, marks 
FROM students 
WHERE id = 1;

-- 2. Select Multiple Specific IDs using IN Clause
SELECT id, name, email 
FROM students 
WHERE id IN (1, 3, 5);

-- 3. Parameterized Node.js mysql2 prepared query string
-- SELECT id, name, email, course, marks FROM students WHERE id = ?;
