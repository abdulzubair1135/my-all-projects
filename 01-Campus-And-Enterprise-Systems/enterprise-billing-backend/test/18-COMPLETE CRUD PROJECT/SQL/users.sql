-- SQL Script for Complete CRUD Project
-- Create Database
CREATE DATABASE IF NOT EXISTS crud_db;
USE crud_db;

-- Create Users Table
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  age INT NOT NULL,
  city VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Initial Sample Data
INSERT INTO users (name, email, age, city) VALUES
('Rahul Sharma', 'rahul@example.com', 22, 'Delhi'),
('Priya Verma', 'priya@example.com', 21, 'Mumbai'),
('Amit Patel', 'amit@example.com', 23, 'Ahmedabad');
