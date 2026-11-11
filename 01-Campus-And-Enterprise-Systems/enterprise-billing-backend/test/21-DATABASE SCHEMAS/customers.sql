-- Table Schema for customers table
-- Used in Billing, CRM, and Order Management Systems

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE DEFAULT NULL,
    address TEXT,
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Insert Data
INSERT INTO customers (name, phone, email, address, loyalty_points) VALUES
('Rahul Sharma', '9876543210', 'rahul@example.com', '123 Main St, New Delhi', 50),
('Priya Singh', '9876543211', 'priya@example.com', '456 Park Ave, Mumbai', 120);
