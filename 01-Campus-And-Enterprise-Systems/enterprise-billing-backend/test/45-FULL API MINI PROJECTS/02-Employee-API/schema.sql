CREATE DATABASE IF NOT EXISTS employee_db;
USE employee_db;

CREATE TABLE IF NOT EXISTS employees (
  id INT AUTO_INCREMENT PRIMARY KEY,
  emp_code VARCHAR(20) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  designation VARCHAR(50) NOT NULL,
  salary DECIMAL(10,2) NOT NULL,
  department VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO employees (emp_code, name, email, designation, salary, department) VALUES
('EMP001', 'Vikram Singh', 'vikram@company.com', 'Software Engineer', 65000.00, 'IT'),
('EMP002', 'Neha Gupta', 'neha@company.com', 'HR Manager', 55000.00, 'HR'),
('EMP003', 'Rohan Mehta', 'rohan@company.com', 'DevOps Lead', 80000.00, 'IT');
