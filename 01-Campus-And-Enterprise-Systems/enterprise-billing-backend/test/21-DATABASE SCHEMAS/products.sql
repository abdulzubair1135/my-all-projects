-- Table Schema for products table
-- Used in Inventory, POS, E-commerce, and Billing Exam Questions

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0,
    barcode VARCHAR(50) UNIQUE DEFAULT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Insert Data
INSERT INTO products (name, category, price, stock, barcode) VALUES
('Wireless Mouse', 'Electronics', 499.00, 50, '8901234567890'),
('Mechanical Keyboard', 'Electronics', 2499.00, 25, '8901234567891'),
('Notebook A5', 'Stationery', 120.00, 100, '8901234567892');
