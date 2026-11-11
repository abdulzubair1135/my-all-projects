CREATE DATABASE IF NOT EXISTS college_db;
USE college_db;

CREATE TABLE IF NOT EXISTS departments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dept_name VARCHAR(100) NOT NULL UNIQUE,
  dept_code VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS courses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  course_code VARCHAR(20) NOT NULL UNIQUE,
  course_name VARCHAR(100) NOT NULL,
  credits INT NOT NULL,
  department_id INT NOT NULL,
  FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

INSERT INTO departments (dept_name, dept_code) VALUES
('Computer Science', 'CS'),
('Information Technology', 'IT'),
('Management Studies', 'MS');

INSERT INTO courses (course_code, course_name, credits, department_id) VALUES
('CS101', 'Data Structures & Algorithms', 4, 1),
('CS102', 'Web Development with Node.js', 4, 1),
('IT201', 'Cloud Computing Basics', 3, 2),
('MS301', 'Financial Accounting', 3, 3);
