-- Create Database
CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Create Students Table
CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  roll_no VARCHAR(20) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  department VARCHAR(50) NOT NULL,
  gpa DECIMAL(3,2) NOT NULL DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed Data
INSERT INTO students (roll_no, name, email, department, gpa) VALUES
('BCA101', 'Rahul Sharma', 'rahul@example.com', 'Computer Science', 8.50),
('BCA102', 'Priya Patel', 'priya@example.com', 'Information Technology', 9.10),
('BCA103', 'Amit Kumar', 'amit@example.com', 'Computer Science', 7.80);
