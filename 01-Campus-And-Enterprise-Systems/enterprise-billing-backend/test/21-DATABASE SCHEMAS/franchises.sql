-- Table Schema for franchises table
-- Used in Franchise Management / Multi-outlet Store Exam Questions

CREATE TABLE IF NOT EXISTS franchises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    owner_name VARCHAR(100) NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    status ENUM('active', 'inactive', 'pending') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Insert Data
INSERT INTO franchises (name, code, owner_name, contact_number, city, address) VALUES
('Delhi Hub', 'FR-DEL-01', 'Amit Kumar', '9811122233', 'Delhi', 'Connaught Place, New Delhi'),
('Mumbai Central', 'FR-MUM-01', 'Neha Verma', '9822233344', 'Mumbai', 'Bandra West, Mumbai');
