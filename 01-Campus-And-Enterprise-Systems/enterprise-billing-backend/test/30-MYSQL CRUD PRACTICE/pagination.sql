-- SQL Server-Side Pagination Formula Practice

-- Formula for Pagination:
-- LIMIT = page_size
-- OFFSET = (page_number - 1) * page_size

-- Assume page_size = 10 items per page

-- Page 1: (1 - 1) * 10 = 0 OFFSET
SELECT * FROM students 
ORDER BY id ASC 
LIMIT 10 OFFSET 0;

-- Page 2: (2 - 1) * 10 = 10 OFFSET
SELECT * FROM students 
ORDER BY id ASC 
LIMIT 10 OFFSET 10;

-- Page 3: (3 - 1) * 10 = 20 OFFSET
SELECT * FROM students 
ORDER BY id ASC 
LIMIT 10 OFFSET 20;

-- Parameterized Node.js mysql2 calculation example:
-- const limit = parseInt(req.query.limit) || 10;
-- const page = parseInt(req.query.page) || 1;
-- const offset = (page - 1) * limit;
-- const sql = 'SELECT * FROM students ORDER BY id ASC LIMIT ? OFFSET ?';
-- pool.query(sql, [limit, offset]);
