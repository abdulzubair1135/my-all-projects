-- INNER JOIN Practice
-- Setup Schema Assumption
-- students: id, name, email, department_id
-- departments: id, dept_name, location

CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL,
    location VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- INNER JOIN: Returns records that have matching values in both tables only.
SELECT 
    s.id AS student_id,
    s.name AS student_name,
    s.email,
    d.dept_name,
    d.location
FROM students s
INNER JOIN departments d ON s.department_id = d.id;
