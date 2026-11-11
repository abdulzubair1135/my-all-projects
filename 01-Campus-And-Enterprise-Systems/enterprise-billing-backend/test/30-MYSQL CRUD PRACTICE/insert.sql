-- SQL Insert Statements Practice
-- Database Table Setup Assumption
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    course VARCHAR(50) NOT NULL,
    marks INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1. Insert Single Record
INSERT INTO students (name, email, course, marks) 
VALUES ('Rahul Sharma', 'rahul@example.com', 'BCA', 85);

-- 2. Insert Multiple Records (Bulk Insert)
INSERT INTO students (name, email, course, marks) VALUES 
('Priya Singh', 'priya@example.com', 'BCA', 92),
('Amit Kumar', 'amit@example.com', 'MCA', 78),
('Sneha Patel', 'sneha@example.com', 'BCA', 64),
('Vikas Verma', 'vikas@example.com', 'BTech', 88);

-- 3. Parameterized SQL Template (Used in Node.js mysql2)
-- INSERT INTO students (name, email, course, marks) VALUES (?, ?, ?, ?);
