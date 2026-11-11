-- SQL WHERE Clause Filtering Practice

-- 1. Equal To (=)
SELECT * FROM students WHERE course = 'BCA';

-- 2. Greater Than / Less Than (> , < , >= , <=)
SELECT * FROM students WHERE marks >= 80;

-- 3. AND Operator (Both conditions must be true)
SELECT * FROM students WHERE course = 'BCA' AND marks >= 85;

-- 4. OR Operator (At least one condition must be true)
SELECT * FROM students WHERE course = 'BCA' OR course = 'MCA';

-- 5. NOT Operator
SELECT * FROM students WHERE NOT course = 'BTech';

-- 6. BETWEEN Operator (Inclusive range)
SELECT * FROM students WHERE marks BETWEEN 70 AND 90;

-- 7. LIKE Operator (Pattern Matching with wildcards % and _)
-- % matches 0 or more characters, _ matches exactly 1 character
SELECT * FROM students WHERE name LIKE 'P%';       -- Starts with P
SELECT * FROM students WHERE email LIKE '%@gmail.com'; -- Gmail address
SELECT * FROM students WHERE name LIKE '_r%';      -- 2nd letter is 'r'

-- 8. IS NULL / IS NOT NULL
SELECT * FROM students WHERE marks IS NOT NULL;
