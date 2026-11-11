-- SQL LIMIT & OFFSET Practice

-- 1. Fetch First 3 Records
SELECT * FROM students 
LIMIT 3;

-- 2. Fetch Top 3 Scorers (Combine ORDER BY and LIMIT)
SELECT * FROM students 
ORDER BY marks DESC 
LIMIT 3;

-- 3. Fetch Records using OFFSET (Skip first 2 records, fetch next 3)
SELECT * FROM students 
ORDER BY id ASC 
LIMIT 3 OFFSET 2;

-- Alternative Short Syntax: LIMIT offset, count
SELECT * FROM students 
ORDER BY id ASC 
LIMIT 2, 3;
