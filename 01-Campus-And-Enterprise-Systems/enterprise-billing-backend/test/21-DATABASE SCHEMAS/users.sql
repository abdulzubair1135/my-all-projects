-- Table Schema for users table
-- Used for Authentication, User Management, and Role-Based Access Control in Exam Projects

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'staff', 'customer') DEFAULT 'customer',
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Insert Statements for Testing
INSERT INTO users (name, email, password, role) VALUES 
('Admin User', 'admin@example.com', '$2b$10$e8w.x7W39Xz3gUuP11nCse3xH9WqV0/J1Y0/7Y5w5m4U.1q8J9y2S', 'admin'),
('John Staff', 'john@example.com', '$2b$10$e8w.x7W39Xz3gUuP11nCse3xH9WqV0/J1Y0/7Y5w5m4U.1q8J9y2S', 'staff');
